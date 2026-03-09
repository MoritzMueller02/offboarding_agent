from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from supabase import Client
from uuid import UUID, uuid4

from app.dependencies import get_db
from app.db.repositories.audio_recordings_repository import AudioRecordingsClient
from app.models.schema import AudioUploadResponse

router = APIRouter()

ALLOWED_MIME_TYPES = {"audio/mpeg", "audio/wav", "audio/aac", "audio/mp4", "audio/ogg", "audio/webm"}
MAX_FILE_SIZE = 50_000_000  # 50 MB


@router.post("/upload", response_model=AudioUploadResponse, status_code=201)
async def upload_audio(
    file: UploadFile = File(...),      # die Datei selbst
    session_id: UUID = Form(...),      # zu welcher Session
    db: Client = Depends(get_db),
):
    """Upload an audio file to Supabase Storage and save metadata to DB."""

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 50 MB.")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {file.content_type}")

    # Eindeutiger Pfad im Storage-Bucket: sessions/{session_id}/{uuid}_{filename}
    storage_path = f"{session_id}/{uuid4()}_{file.filename}"

    db.storage.from_("audio-recordings").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": file.content_type},
    )

    repo = AudioRecordingsClient(db)
    recording = repo.create(
        session_id=session_id,
        storage_path=storage_path,
        file_name=file.filename,
        file_size=len(file_bytes),
        mime_type=file.content_type,
    )

    return AudioUploadResponse(
        audio_id=recording["id"],
        file_name=recording["file_name"],
        file_size=recording["file_size"],
        storage_path=recording["storage_path"],
        processing_status=recording["processing_status"],
    )


@router.get("/{recording_id}", response_model=AudioUploadResponse)
def get_recording(recording_id: UUID, db: Client = Depends(get_db)):
    """Get a single audio recording by ID."""
    repo = AudioRecordingsClient(db)
    recording = repo.get_by_id(recording_id)

    if not recording:
        raise HTTPException(status_code=404, detail="Audio recording not found")

    return AudioUploadResponse(
        audio_id=recording["id"],
        file_name=recording["file_name"],
        file_size=recording["file_size"],
        storage_path=recording["storage_path"],
        processing_status=recording["processing_status"],
    )
