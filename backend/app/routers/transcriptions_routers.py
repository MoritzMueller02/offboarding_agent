# app/routers/transcriptions.py

from fastapi import APIRouter, Depends, HTTPException, Request
from supabase import Client
from uuid import UUID
from typing import List

from app.dependencies import get_db
from app.db.repositories.transcriptions_repository import TranscriptionRepository
from app.db.repositories.audio_recordings_repository import AudioRecordingsClient
from app.models.schema import TranscriptionResponse 
from app.services.transcription import Speech2Text


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

@router.post("/audio/{audio_id}", response_model = TranscriptionResponse)
async def transcribe(audio_id: UUID, request: Request, db = Depends(get_db)):
    
    audio_repo = AudioRecordingsClient(db)
    recording = audio_repo.get_by_id(audio_id)
    
    if not recording:
        raise HTTPException(status_code=404, detail = "Recording not found")
    
    audio_bytes = db.storage.from_("audio-recordings").download(recording["storage_path"])
    model = request.app.state.speech_model
    transcription = model.transcribe_audio(audio_bytes)
    trans_repo = TranscriptionRepository(db)
    
    saved = trans_repo.create(
        audio_recording_id=audio_id,
        text = transcription,
        model_name = Speech2Text.MODEL_NAME
    )
    
    return TranscriptionResponse(**saved)
