"""Pydantic models for source verification and tracking."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class VerifiedSource(BaseModel):
    """Model for verified source information."""
    
    claim: str
    footnote_number: Optional[int] = None
    source_url: str
    source_type: str  # "government_regulation", "industry_report", "academic"
    authority_level: str  # "high", "medium", "low"
    accessed_at: datetime
    verified: bool
    confidence_level: str  # "high", "medium", "low"
    cross_verified_count: int = 0
    content_snippet: Optional[str] = None
    agent_notes: Optional[str] = None
    search_queries_used: List[str]
    verification_status: str  # "verified", "partial", "unverified"


class SourceMetadata(BaseModel):
    """Model for complete source metadata file."""
    
    brd_id: Optional[str] = None
    prd_id: Optional[str] = None
    project_name: str
    generated_at: datetime
    sources_used: List[VerifiedSource]
    search_statistics: dict
    data_integrity: dict
