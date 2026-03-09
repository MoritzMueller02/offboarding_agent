from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.dependencies import get_db
from app.db.repositories.sessions_repository import SessionRepository
from app.models.schema import Session, SessionCreate

router = APIRouter()


class SessionStatusUpdate(BaseModel):
    status: str
    progress_percentage: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@router.post("/", response_model=Session, status_code=201)
def create_session(payload: SessionCreate, db: Client = Depends(get_db)):
    """Create a new offboarding session"""
    repo = SessionRepository(db)

    return repo.create(
        employee_id=payload.employee_id,
        title=payload.title,
        session_type=payload.session_type,
        description=payload.description,
        scheduled_at=payload.scheduled_at.isoformat() if payload.scheduled_at else None,
    )


@router.get("/employee/{employee_id}", response_model=List[Session])
def list_by_employee(employee_id: UUID, db: Client = Depends(get_db)):
    """List all sessions for an employee"""
    return SessionRepository(db).list_by_employee(employee_id)


@router.get("/{session_id}", response_model=Session)
def get_session(session_id: UUID, db: Client = Depends(get_db)):
    """Get a session by ID"""
    repo = SessionRepository(db)
    session = repo.get_by_id(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.patch("/{session_id}/status", response_model=Session)
def update_session_status(
    session_id: UUID,
    payload: SessionStatusUpdate,
    db: Client = Depends(get_db),
):
    """Update the status and progress of a session"""
    valid = ('scheduled', 'in_progress', 'completed', 'cancelled')
    if payload.status not in valid:
        raise HTTPException(status_code=422, detail=f"Invalid status. Must be one of: {valid}")

    repo = SessionRepository(db)

    if not repo.get_by_id(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    return repo.update_status(
        id=session_id,
        status=payload.status,
        progress_percentage=payload.progress_percentage,
        started_at=payload.started_at.isoformat() if payload.started_at else None,
        completed_at=payload.completed_at.isoformat() if payload.completed_at else None,
    )
