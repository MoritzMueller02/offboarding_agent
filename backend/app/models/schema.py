"""
Pydantic models for request/response validation.
These define the shape of data in your API.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID


# ============================================
# Base Models (für Wiederverwendung)
# ============================================

class TimestampMixin(BaseModel):
    """Mixin for created_at/updated_at"""
    created_at: datetime
    updated_at: datetime


# ============================================
# Employee Models
# ============================================

class EmployeeBase(BaseModel):
    """Shared employee fields"""
    email: EmailStr
    first_name: str
    last_name: str
    department: Optional[str] = None
    position: Optional[str] = None
    employee_id: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    """Employee creation (from client)"""
    employment_status: str = "active"


class EmployeeUpdate(BaseModel):
    """Employee update (partial)"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    employment_status: Optional[str] = None


class Employee(EmployeeBase, TimestampMixin):
    """Employee response (to client)"""
    id: UUID
    employment_status: str
    offboarding_date: Optional[datetime] = None
    last_working_day: Optional[datetime] = None
    
    # Allow ORM mode (from Supabase)
    model_config = ConfigDict(from_attributes=True)



class SessionBase(BaseModel):
    """Shared session fields"""
    title: str
    description: Optional[str] = None
    session_type: str = Field(..., pattern="^(exit_interview|knowledge_transfer|skills_review|project_handover)$")


class SessionCreate(SessionBase):
    """Session creation"""
    employee_id: UUID
    scheduled_at: Optional[datetime] = None


class Session(SessionBase, TimestampMixin):
    """Session response"""
    id: UUID
    employee_id: UUID
    status: str
    progress_percentage: int
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)



class AudioUploadResponse(BaseModel):
    """Response after audio upload"""
    audio_id: UUID
    file_name: str
    file_size: int
    storage_path: str
    processing_status: str


class TranscriptionResponse(BaseModel):
    """Transcription result"""
    transcription_id: UUID
    audio_recording_id: UUID
    text: str
    language: str
    confidence_score: Optional[float]




class SearchRequest(BaseModel):
    """Knowledge search request"""
    query: str = Field(..., min_length=3, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)
    filters: Optional[dict] = None


class SearchResult(BaseModel):
    """Single search result"""
    chunk_id: UUID
    chunk_text: str
    similarity: float
    metadata: dict
    source_type: str


class SearchResponse(BaseModel):
    """Search results"""
    query: str
    results: List[SearchResult]
    count: int