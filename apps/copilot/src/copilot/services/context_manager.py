from typing import Dict, Optional
from datetime import datetime


class ContextManager:
    """Manage in-memory session state"""

    def __init__(self):
        self.sessions: Dict[str, dict] = {}

    def init_session(
        self,
        project_name: str,
        user_id: str,
        problem_statement: str
    ) -> None:
        """Initialize new session"""
        self.sessions[project_name] = {
            "user_id": user_id,
            "problem_statement": problem_statement,
            "stage": "ba",  # ba → ba_approval → pe → pe_approval → done
            "ba_output": None,
            "pe_output": None,
            "feedback": None,
            "created_at": datetime.now(),
            "history": []  # Track all feedback/outputs
        }

    def get_session(self, project_name: str) -> Optional[dict]:
        """Retrieve session by project name"""
        return self.sessions.get(project_name)

    def update_session(self, project_name: str, key: str, value) -> None:
        """Update session value"""
        if project_name in self.sessions:
            self.sessions[project_name][key] = value

    def add_to_history(
        self,
        project_name: str,
        stage: str,
        output: str,
        feedback: Optional[str] = None
    ) -> None:
        """Track feedback/output history"""
        if project_name in self.sessions:
            self.sessions[project_name]["history"].append({
                "stage": stage,
                "output": output,
                "feedback": feedback,
                "timestamp": datetime.now()
            })

    def session_exists(self, project_name: str) -> bool:
        """Check if session exists"""
        return project_name in self.sessions