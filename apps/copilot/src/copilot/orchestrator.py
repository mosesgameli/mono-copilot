from enum import Enum
from typing import Optional, Dict
from datetime import datetime
import json
from pathlib import Path

from .services.context_manager import ContextManager
from .services.file_manager import FileManager
from .agents.ba_agent import BAAgent
from .agents.pe_agent import PEAgent


class OrchestratorState(Enum):
    BA_PENDING = "ba_pending"
    BA_APPROVAL = "ba_approval"
    BA_CLARIFYING = "ba_clarifying"
    BA_REWORKING = "ba_reworking"
    BA_DEEP_DIVE = "ba_deep_dive"
    BA_FAILED = "ba_failed"
    PE_PENDING = "pe_pending"
    PE_APPROVAL = "pe_approval"
    PE_CLARIFYING = "pe_clarifying"
    PE_REWORKING = "pe_reworking"
    PE_DEEP_DIVE = "pe_deep_dive"
    PE_FAILED = "pe_failed"
    PE_JUMP_BACK_TO_BA = "pe_jump_back_to_ba"
    DONE = "done"


class Orchestrator:
    
    def __init__(self):
        self.context_manager = ContextManager()
        self.file_manager = FileManager()
        self.ba_agent = BAAgent()
        self.pe_agent = PEAgent()
        self.max_reruns = 5
        self.max_attempts = 9
    
    async def process_input(
        self,
        project_name: str,
        user_id: str,
        problem_statement: str,
        segment: str
    ) -> Dict:
        
        # First check if project already exists
        existing_session = self.context_manager.get_session(project_name)
        if existing_session:
            return {
                "status": "error",
                "message": f"Project {project_name} already exists",
                "stage": "error"
            }
        
        # Initialize new session
        self.context_manager.init_session(
            project_name=project_name,
            user_id=user_id,
            problem_statement=problem_statement
        )
        
        # Update session with BA input
        self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_PENDING.value)
        self.context_manager.update_session(project_name, "segment", segment)
        self.context_manager.update_session(project_name, "run_count", 1)
        
        # Call BA agent
        ba_result = await self.ba_agent.run(
            problem_statement=problem_statement,
            segment=segment,
            run_count=1
        )
        
        if not ba_result or ba_result.get("status") == "error":
            self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_FAILED.value)
            return {
                "status": "error",
                "message": "BA agent failed to generate BRD",
                "stage": "ba_failed"
            }
        
        # Save BRD to file
        brd_markdown = ba_result.get("markdown", "")
        self.file_manager.save_brd(project_name, brd_markdown)
        
        # Store BRD output in session
        self.context_manager.update_session(project_name, "ba_output", ba_result)
        self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_APPROVAL.value)
        
        # Add to history
        self.context_manager.add_to_history(
            project_name=project_name,
            stage="ba",
            output=brd_markdown
        )
        
        return {
            "status": "success",
            "stage": "ba_approval",
            "document_id": ba_result.get("document_id"),
            "output": brd_markdown,
            "approval_required": True,
            "message": "BRD generated. Please review and approve or provide feedback."
        }
    
    async def handle_approval(
        self,
        project_name: str,
        stage: str,
        decision: str,
        feedback: Optional[str] = None
    ) -> Dict:
        
        session = self.context_manager.get_session(project_name)
        if not session:
            return {
                "status": "error",
                "message": f"Project {project_name} not found",
                "stage": "error"
            }
        
        current_stage = session.get("stage")
        
        # Handle BA approval
        if stage == "ba":
            if current_stage != OrchestratorState.BA_APPROVAL.value:
                return {
                    "status": "error",
                    "message": f"Cannot approve BA at stage {current_stage}",
                    "stage": current_stage
                }
            
            if decision == "approve":
                self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_PENDING.value)
                self.context_manager.update_session(project_name, "run_count", 1)
                
                # Call PE agent with BRD context
                ba_output = session.get("ba_output")
                pe_result = await self.pe_agent.run(
                    brd_dict=ba_output,
                    run_count=1
                )
                
                if not pe_result or pe_result.get("status") == "error":
                    self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_FAILED.value)
                    return {
                        "status": "error",
                        "message": "PE agent failed to generate PRD",
                        "stage": "pe_failed"
                    }
                
                prd_markdown = pe_result.get("markdown", "")
                self.file_manager.save_prd(project_name, prd_markdown)
                self.context_manager.update_session(project_name, "pe_output", pe_result)
                self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_APPROVAL.value)
                
                self.context_manager.add_to_history(
                    project_name=project_name,
                    stage="pe",
                    output=prd_markdown
                )
                
                return {
                    "status": "success",
                    "stage": "pe_approval",
                    "document_id": pe_result.get("document_id"),
                    "output": prd_markdown,
                    "approval_required": True,
                    "message": "PRD generated. Please review and approve or provide feedback."
                }
            
            elif decision == "needs_changes" or decision == "clarification":
                self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_CLARIFYING.value)
                
                questions = await self.get_clarification_questions(project_name, "ba")
                return {
                    "status": "success",
                    "stage": "ba_clarifying",
                    "questions": questions,
                    "message": "Please answer the following questions to help improve the BRD."
                }
        
        # Handle PE approval
        elif stage == "pe":
            if current_stage != OrchestratorState.PE_APPROVAL.value:
                return {
                    "status": "error",
                    "message": f"Cannot approve PE at stage {current_stage}",
                    "stage": current_stage
                }
            
            if decision == "approve":
                self.context_manager.update_session(project_name, "stage", OrchestratorState.DONE.value)
                return {
                    "status": "success",
                    "stage": "done",
                    "message": "Workflow complete! Both BRD and PRD have been approved."
                }
            
            elif decision == "jump_back_to_ba":
                self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_JUMP_BACK_TO_BA.value)
                return {
                    "status": "success",
                    "stage": "pe_jump_back_to_ba",
                    "message": "Jumping back to BA. You can now modify the BRD. Run /agent/approve with stage='ba' and decision='approve' when ready."
                }
            
            elif decision == "needs_changes" or decision == "clarification":
                self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_CLARIFYING.value)
                
                questions = await self.get_clarification_questions(project_name, "pe")
                return {
                    "status": "success",
                    "stage": "pe_clarifying",
                    "questions": questions,
                    "message": "Please answer the following questions to help improve the PRD."
                }
        
        return {
            "status": "error",
            "message": "Invalid stage or decision",
            "stage": current_stage
        }
    
    async def get_clarification_questions(
        self,
        project_name: str,
        stage: str
    ) -> list:
        
        session = self.context_manager.get_session(project_name)
        if not session:
            return []
        
        # These are generic questions. In production, these would be generated
        # by analyzing the output and identifying gaps
        
        if stage == "ba":
            questions = [
                "Are there any specific regulatory requirements or compliance considerations for this business problem?",
                "What is the expected timeline and budget for implementing this solution?",
                "Who are the key stakeholders that need to be involved in this process?"
            ]
        elif stage == "pe":
            questions = [
                "What are the critical performance requirements (latency, throughput, availability)?",
                "Do you have any constraints on technology choices or existing systems we must integrate with?",
                "What disaster recovery and backup strategies should we consider?"
            ]
        else:
            questions = []
        
        return questions
    
    async def handle_clarification_response(
        self,
        project_name: str,
        stage: str,
        responses: Dict
    ) -> Dict:
        
        session = self.context_manager.get_session(project_name)
        if not session:
            return {
                "status": "error",
                "message": f"Project {project_name} not found",
                "stage": "error"
            }
        
        current_stage = session.get("stage")
        current_run = session.get("run_count", 1)
        
        # Build feedback string from responses
        feedback_parts = []
        for key, value in responses.items():
            feedback_parts.append(f"{key}: {value}")
        feedback = "\n".join(feedback_parts)
        
        # Handle BA clarification
        if stage == "ba" and current_stage == OrchestratorState.BA_CLARIFYING.value:
            
            # Check if we're in deep dive or regular rework
            is_deep_dive = current_run > self.max_reruns
            
            self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_REWORKING.value)
            current_run += 1
            self.context_manager.update_session(project_name, "run_count", current_run)
            
            # Get original problem statement
            problem_statement = session.get("problem_statement")
            segment = session.get("segment")
            
            # Re-run BA agent with clarification feedback
            ba_result = await self.ba_agent.run(
                problem_statement=problem_statement,
                segment=segment,
                clarification_feedback=feedback,
                run_count=current_run
            )
            
            if not ba_result or ba_result.get("status") == "error":
                # Check if we've exceeded max attempts
                if current_run >= self.max_attempts:
                    self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_FAILED.value)
                    return {
                        "status": "error",
                        "message": "BA agent could not generate satisfactory BRD after multiple attempts. Consider revising the problem statement.",
                        "stage": "ba_failed"
                    }
                else:
                    # Move to deep dive if we've hit the rerun limit
                    if current_run == self.max_reruns + 1:
                        self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_DEEP_DIVE.value)
                        return {
                            "status": "success",
                            "stage": "ba_deep_dive",
                            "message": "We need to go deeper. Please provide more detailed answers to these questions.",
                            "questions": await self.get_clarification_questions(project_name, "ba")
                        }
                    else:
                        self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_APPROVAL.value)
                        return {
                            "status": "success",
                            "stage": "ba_approval",
                            "output": session.get("ba_output", {}).get("markdown", ""),
                            "message": "Could not improve BRD further. Please review the current version.",
                            "approval_required": True
                        }
            
            # Save updated BRD
            brd_markdown = ba_result.get("markdown", "")
            self.file_manager.save_brd(project_name, brd_markdown)
            self.context_manager.update_session(project_name, "ba_output", ba_result)
            self.context_manager.update_session(project_name, "stage", OrchestratorState.BA_APPROVAL.value)
            
            self.context_manager.add_to_history(
                project_name=project_name,
                stage="ba_rework",
                output=brd_markdown,
                feedback=feedback
            )
            
            return {
                "status": "success",
                "stage": "ba_approval",
                "document_id": ba_result.get("document_id"),
                "output": brd_markdown,
                "approval_required": True,
                "run_number": current_run,
                "message": f"BRD updated (attempt {current_run}). Please review and approve or provide more feedback."
            }
        
        # Handle PE clarification
        elif stage == "pe" and current_stage == OrchestratorState.PE_CLARIFYING.value:
            
            self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_REWORKING.value)
            current_run += 1
            self.context_manager.update_session(project_name, "run_count", current_run)
            
            ba_output = session.get("ba_output")
            
            # Re-run PE agent with clarification feedback
            pe_result = await self.pe_agent.run(
                brd_dict=ba_output,
                clarification_feedback=feedback,
                run_count=current_run
            )
            
            if not pe_result or pe_result.get("status") == "error":
                if current_run >= self.max_attempts:
                    self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_FAILED.value)
                    return {
                        "status": "error",
                        "message": "PE agent could not generate satisfactory PRD after multiple attempts. Consider revising the BRD.",
                        "stage": "pe_failed"
                    }
                else:
                    if current_run == self.max_reruns + 1:
                        self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_DEEP_DIVE.value)
                        return {
                            "status": "success",
                            "stage": "pe_deep_dive",
                            "message": "We need to go deeper. Please provide more detailed answers to these questions.",
                            "questions": await self.get_clarification_questions(project_name, "pe")
                        }
                    else:
                        self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_APPROVAL.value)
                        return {
                            "status": "success",
                            "stage": "pe_approval",
                            "output": session.get("pe_output", {}).get("markdown", ""),
                            "message": "Could not improve PRD further. Please review the current version.",
                            "approval_required": True
                        }
            
            # Save updated PRD
            prd_markdown = pe_result.get("markdown", "")
            self.file_manager.save_prd(project_name, prd_markdown)
            self.context_manager.update_session(project_name, "pe_output", pe_result)
            self.context_manager.update_session(project_name, "stage", OrchestratorState.PE_APPROVAL.value)
            
            self.context_manager.add_to_history(
                project_name=project_name,
                stage="pe_rework",
                output=prd_markdown,
                feedback=feedback
            )
            
            return {
                "status": "success",
                "stage": "pe_approval",
                "document_id": pe_result.get("document_id"),
                "output": prd_markdown,
                "approval_required": True,
                "run_number": current_run,
                "message": f"PRD updated (attempt {current_run}). Please review and approve or provide more feedback."
            }
        
        return {
            "status": "error",
            "message": "Invalid state for clarification response",
            "stage": current_stage
        }
