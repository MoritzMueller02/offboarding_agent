# app/routers/transcriptions.py

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from uuid import UUID
from typing import List

from app.dependencies import get_db
from app.db.repositories.transcriptions_repository import TranscriptionRepository
from app.models.schema import TranscriptionResponse  
router = APIRouter()


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
def get_transcription(
    transcription_id: UUID,
    db: Client = Depends(get_db)
):
    """Get a single transcription by ID"""
    repo = TranscriptionRepository(db)
    transcription = repo.get_by_id(transcription_id)
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return transcription


@router.get("/audio/{audio_id}", response_model=TranscriptionResponse)
def get_transcription_by_audio(
    audio_id: UUID,
    db: Client = Depends(get_db)
):
    """Get transcription for a specific audio recording"""
    repo = TranscriptionRepository(db)
    transcription = repo.get_by_audio_id(audio_id)
    
    if not transcription:
        raise HTTPException(status_code=404, detail="No transcription found for this audio")
    
    return transcription


