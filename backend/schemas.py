"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime
from schemas_ast import ClauseNode

class Definition(BaseModel):
    term: str
    definition: str
    section: str

class TimelineStep(BaseModel):
    id: int
    type: Literal["system", "success", "loading", "warning", "complete"]
    title: str
    message: str
    timestamp: str

class Scenario(BaseModel):
    id: str
    name: str
    status: Literal["pass", "fail"]
    description: str
    trigger_event: Optional[str] = None
    conflict: Optional[str] = None
    outcome: Optional[str] = None
    expected_outcome: Optional[str] = None

class ConflictAnalysis(BaseModel):
    has_conflict: bool
    conflict_type: Optional[str] = None
    severity: Optional[Literal["high", "medium", "low"]] = None
    details: Optional[str] = None
    affected_sections: List[str] = []

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    length: int
    preview: str
    uploaded_at: str

class AnalysisResponse(BaseModel):
    document_id: str
    analysis_id: str
    timeline: List[dict]
    scenarios: List[dict]
    tree: Optional[ClauseNode] = None
    analysis_complete: bool
    created_at: str

class DocumentListItem(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    file_type: str
    analysis_count: int


class HealthCheckResponse(BaseModel):
    status: str
    database: str
    mistral_configured: bool
