from pydantic import BaseModel
from typing import Optional


class ApprovalDecision(BaseModel):
    """Decision to proceed or rerun"""
    approved: bool
    reason: Optional[str] = None
    next_stage: Optional[str] = None