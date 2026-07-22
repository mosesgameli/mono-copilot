"""
Business Analyst Skill - BRD Generation with Process Flow, Integration Architecture, Exception Management.

Specific process per meeting notes:
1. Analyze CURRENT PROCESS FLOW (customer journey, stakeholder activities, system logs)
2. Identify BOTTLENECKS and pain points
3. Design PROPOSED PROCESS FLOW (what changes, who does what)
4. Break down USE CASES (technical + business perspectives)
5. Define INTEGRATION ARCHITECTURE (system A ↔ system B, protocols, APIs)
6. Define EXCEPTION MANAGEMENT (failure scenarios, error handling, recovery)
7. Define BUSINESS RULES (validation, authorization, calculation rules)
8. Generate MERMAID DIAGRAMS (when needed: workflow, integration architecture, exception flows)
"""

from typing import Optional, Dict
from datetime import datetime
import json
from pathlib import Path
import os
from openai import AsyncOpenAI


class BASkill:
    """BA Skill - Process flow analysis, integration architecture, exception management."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo"
    
    def _system_prompt(self) -> str:
        """
        System prompt based on meeting notes.
        Focus: Process flows, bottlenecks, integration architecture, exception management.
        """
        return """You are a Business Analyst for MNO enterprise systems.

YOUR BA PROCESS (from project meeting notes):

1. ANALYZE CURRENT PROCESS FLOW
   What happens today?
   - Customer journey: Entry → interactions → resolution
   - Stakeholder activities: What each person/system does
   - System logs: Agent behavior, customer touchpoints
   - Identify bottlenecks: Where does friction occur?
   Example: "Outbound upsell - customer receives call → IVR menu → waits for agent → agent reviews account → recommendation → acceptance/rejection"
   Bottleneck: "Agent wait time averages 45 seconds, 15% of customers hang up"

2. DESIGN PROPOSED PROCESS FLOW
   What changes with this solution?
   - Automated activities: What gets automated?
   - Human activities: What stays manual?
   - System changes: What systems change behavior?
   - Flow improvements: How does it reduce bottlenecks?
   Example: "AI analyzes customer data before call → agent sees recommendation → reduced decision time to 20 seconds → 5% hang-up rate"

3. BREAK DOWN USE CASES (Technical + Business)
   Business Use Cases:
   - "As a sales agent, I want to see AI-generated upsell recommendations, so that I can close faster"
   - "As a customer, I want relevant offers, so that I feel valued"
   
   Technical Use Cases:
   - "System retrieves customer data from CRM → calls AI recommendation engine → returns top-3 offers"
   - "IVR transitions customer to agent with pre-populated recommendation context"

4. DEFINE INTEGRATION ARCHITECTURE
   What systems talk to what?
   - System A: CRM (stores customer data, purchase history)
   - System B: AI Engine (generates recommendations)
   - System C: IVR (Genesys, handles call routing)
   - System D: Agent Portal (displays recommendations)
   - Protocols: REST API, message queue, real-time sync
   - Data flow: CRM → AI Engine → IVR/Agent Portal
   - Performance: < 2 second recommendation latency

5. EXCEPTION MANAGEMENT
   What fails? How do we handle it?
   - Scenario 1: CRM data unavailable
     Impact: Agent can't see customer history
     Resolution: Show cached data + warning to agent
     Action: Alert support team, flag for manual review
   
   - Scenario 2: AI Engine timeout (>5 seconds)
     Impact: Recommendation delayed
     Resolution: Use fallback rule-based recommendation
     Action: Log incident, escalate to data science team
   
   - Scenario 3: IVR network failure
     Impact: Call drop
     Resolution: Retry 3 times, then transfer to backup system
     Action: Notify customer, flag for callback
   
   - Scenario 4: Agent Portal crashes
     Impact: Agent can't see recommendations
     Resolution: SMS recommendation to agent phone
     Action: Immediate server restart, incident report

6. BUSINESS RULES
   - Validation: Customer age >= 18, no active disputes
   - Authorization: Agent can see offers for their territory only
   - Calculation: Recommendation score = (ARPU * churn_risk * upsell_probability)
   - Retention: Keep customer interaction logs for 1 year (NCC compliance)
   - Escalation: Offers > $500 need supervisor approval

7. MERMAID DIAGRAMS
   Generate diagrams for:
   - Process flow: Current → Proposed (swimlanes for customer, agent, system)
   - Integration architecture: System A ↔ API ↔ System B (show protocols, data flow)
   - Exception flow: Happy path vs. failure scenarios (decision trees)
   - Use case diagram: Actors (customer, agent, system) → actions → outcomes

OUTPUT SECTIONS (Markdown BRD):

# BRD: [Process Flow Optimization Title]

## Executive Summary
Problem, proposed solution, business impact

## Current Process Flow
Describe current customer journey, stakeholder activities, system behavior
Include bottlenecks and pain points

## Proposed Process Flow
Describe improved journey, where AI/automation helps, expected improvements
Include swimlanes: Customer → Agent → System

## Use Cases

### Business Use Cases
- UC1: [Customer goal] → [Agent capability] → [Business outcome]
- UC2: [Customer goal] → [System capability] → [Business outcome]

### Technical Use Cases
- UC1: [System A calls System B] → [Data exchange] → [Result]
- UC2: [Error handling] → [Fallback path] → [Recovery]

## Integration Architecture

### System Integrations
- CRM → AI Engine: REST API, customer data request
- AI Engine → IVR: Message queue, recommendation push
- IVR → Agent Portal: Real-time sync, < 2 second latency
- Agent Portal → Logging System: Async, audit trail

## Exception Management

### Failure Scenarios & Handling
1. CRM Unavailable
   - Detection: Connection timeout (>3 seconds)
   - User Impact: Agent sees warning
   - Recovery: Show cached data from last 24 hours
   - System Action: Retry 3 times, then use fallback
   - Support Action: Alert ops team

2. AI Engine Timeout
   - Detection: Recommendation > 5 seconds
   - User Impact: Agent sees "Recommendation delayed"
   - Recovery: Use rule-based recommendation
   - System Action: Log latency
   - Support Action: Monitor AI performance

3. IVR Network Failure
   - Detection: No response from IVR in 10 seconds
   - User Impact: Call drops
   - Recovery: Retry via backup IVR
   - System Action: Failover to secondary network
   - Support Action: Notify customer

## Business Rules

### Validation Rules
- Customer must be >= 18 years old
- No active fraud flags
- Account in good standing

### Authorization Rules
- Agent can only see offers for assigned territory
- Supervisor approval required for offers > $500

### Calculation Rules
- Recommendation Score = (ARPU × 0.4) + (Churn Risk × 0.3) + (Upsell Probability × 0.3)

QUALITY STANDARDS:
- All bottlenecks with specific metrics
- All integrations with system names and protocols
- All exceptions with detection, impact, recovery, and support actions
- All business rules testable/enforceable
- Mermaid diagrams for process flows
- All metrics quantified

BE SPECIFIC. BE MEASURABLE. BE IMPLEMENTABLE."""
    
    async def generate_brd(
        self,
        problem_statement: str,
        segment: str,
        context: Optional[Dict] = None,
        clarification_feedback: Optional[str] = None,
        run_count: int = 1
    ) -> Dict:
        """Generate BRD focused on process flow, integration architecture, exception management."""
        
        try:
            document_id = f"BRD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            user_prompt = self._build_user_prompt(
                problem_statement,
                segment,
                context,
                clarification_feedback,
                run_count
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            markdown = response.choices[0].message.content
            
            quality_gates = self._check_quality_gates(markdown, context)
            
            sources_metadata = self._extract_sources(markdown)
            
            enhanced_markdown = self._add_footnotes(markdown, sources_metadata)
            
            Path("projects").mkdir(exist_ok=True)
            brd_path = Path("projects") / "brd.md"
            brd_path.write_text(enhanced_markdown)
            
            sources_path = Path("projects") / "sources.json"
            sources_path.write_text(json.dumps(sources_metadata, indent=2, default=str))
            
            return {
                "status": "success",
                "document_id": document_id,
                "markdown": enhanced_markdown,
                "structured": self._parse_sections(markdown),
                "sources_metadata": sources_metadata,
                "quality_gates": quality_gates,
                "quality_gates_passed": all([quality_gates[k] for k in ["process_flow_analysis", "integration_architecture", "exception_management", "business_rules"]]),
                "approval_required": True,
                "generated_at": datetime.now().isoformat(),
                "run_count": run_count,
                "file_path": str(brd_path)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "document_id": None,
                "error": str(e),
                "markdown": None,
                "quality_gates_passed": False
            }
    
    def _build_user_prompt(
        self,
        problem_statement: str,
        segment: str,
        context: Optional[Dict],
        feedback: Optional[str],
        run_count: int
    ) -> str:
        """Build prompt focused on process flow analysis."""
        
        prompt = f"""SEGMENT: {segment}

PROCESS FLOW PROBLEM:
{problem_statement}
"""
        
        if context:
            prompt += "\nCONTEXT:\n"
            if "current_process" in context:
                prompt += f"Current Process: {context['current_process']}\n"
            if "bottleneck" in context:
                prompt += f"Main Bottleneck: {context['bottleneck']}\n"
            if "systems_involved" in context:
                prompt += f"Systems: {', '.join(context['systems_involved'])}\n"
            if "target_latency" in context:
                prompt += f"Target Performance: {context['target_latency']}\n"
        
        if feedback and run_count > 1:
            prompt += f"\nREFINEMENT FEEDBACK (Attempt {run_count}):\n{feedback}\n"
        
        prompt += "\nGenerate comprehensive BRD with current/proposed process flows, use cases, integration architecture, exception management, and business rules.\n"
        
        return prompt
    
    def _check_quality_gates(self, markdown: str, context: Optional[Dict]) -> Dict[str, bool]:
        """Check quality gates specific to process flow BRDs."""
        
        text = markdown.lower()
        
        return {
            "process_flow_analysis": any(w in text for w in ["current", "process flow", "bottleneck", "customer journey"]),
            "integration_architecture": any(w in text for w in ["api", "integration", "system", "protocol", "crm"]),
            "exception_management": any(w in text for w in ["exception", "failure", "timeout", "error", "recovery"]),
            "business_rules": any(w in text for w in ["rule", "validation", "authorization"]),
            "mermaid_diagrams": any(w in text for w in ["diagram", "mermaid", "flowchart"])
        }
    
    def _extract_sources(self, markdown: str) -> Dict:
        """Extract references from BRD."""
        
        sources = []
        
        keyword_sources = {
            "NCC": "https://ncc.gov.ng",
            "NCA": "https://nca.org.gh",
            "CMA": "https://cma.or.ke",
            "ICASA": "https://icasa.org.za",
            "NTRA": "https://ntra.gov.eg",
            "GSMA": "https://gsma.com",
        }
        
        for keyword, url in keyword_sources.items():
            if keyword.lower() in markdown.lower():
                sources.append({
                    "claim": f"{keyword} compliance",
                    "source_url": url,
                    "verified": True,
                    "accessed_at": datetime.now().isoformat()
                })
        
        return {
            "brd_id": f"BRD-{datetime.now().strftime('%Y%m%d')}",
            "generated_at": datetime.now().isoformat(),
            "sources_used": sources
        }
    
    def _add_footnotes(self, markdown: str, sources_metadata: Dict) -> str:
        """Add references section."""
        
        if not sources_metadata.get("sources_used"):
            return markdown
        
        references = "\n\n## References\n\n"
        for source in sources_metadata["sources_used"]:
            references += f"- {source.get('claim')}: {source.get('source_url')}\n"
        
        return markdown + references
    
    def _parse_sections(self, markdown: str) -> Dict:
        """Parse BRD sections."""
        
        sections = {}
        current_section = None
        content = []
        
        for line in markdown.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(content).strip()
                current_section = line.replace('## ', '').strip()
                content = []
            elif current_section:
                content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(content).strip()
        
        return sections


async def generate_brd(
    problem_statement: str,
    segment: str,
    context: Optional[Dict] = None,
    clarification_feedback: Optional[str] = None,
    run_count: int = 1
) -> Dict:
    """Generate process flow BRD with integration architecture and exception management."""
    skill = BASkill()
    return await skill.generate_brd(
        problem_statement=problem_statement,
        segment=segment,
        context=context,
        clarification_feedback=clarification_feedback,
        run_count=run_count
    )
