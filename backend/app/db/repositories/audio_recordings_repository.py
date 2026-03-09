from typing import Dict, Optional, List, Literal, Any
from uuid import UUID
from supabase import Client


class AudioRecordingsClient:

    def __init__(self, db: Client):
        self.db = db
        self.table_name = "audio_recordings"

    def create(
        self,
        session_id: UUID,
        storage_path: str,
        file_name: str,
        processing_status: Literal['uploaded', 'queued', 'processing', 'completed', 'failed'] = 'uploaded',
        storage_bucket: str = "audio-recordings",
        mime_type: Optional[str] = None,
        sample_rate: Optional[int] = None,
        duration_seconds: Optional[int] = None,
        file_size: Optional[int] = None,
        error_message: Optional[str] = None,
        audio_quality: Optional[Literal['low', 'medium', 'high']] = None,
    ) -> Dict[str, Any]:
        """Save audio recording metadata to the database."""

        data: Dict[str, Any] = {
            "session_id": str(session_id),
            "storage_path": storage_path,
            "storage_bucket": storage_bucket,
            "file_name": file_name,
            "processing_status": processing_status,
        }

        if mime_type is not None:
            data["mime_type"] = mime_type
        if sample_rate is not None:
            data["sample_rate"] = sample_rate
        if duration_seconds is not None:
            data["duration_seconds"] = duration_seconds
        if file_size is not None:
            data["file_size"] = file_size
        if error_message is not None:
            data["error_message"] = error_message
        if audio_quality is not None:
            data["audio_quality"] = audio_quality

        result = self.db.table(self.table_name).insert(data).execute()
        return result.data[0]

    def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        """Fetch a single audio recording by its ID."""
        result = self.db.table(self.table_name).select("*").eq("id", str(id)).execute()

        if not result.data:
            return None

        return result.data[0]

    def list_by_session(self, session_id: UUID) -> List[Dict[str, Any]]:
        """List all audio recordings for a given session."""
        result = (
            self.db.table(self.table_name)
            .select("*")
            .eq("session_id", str(session_id))
            .execute()
        )
        return result.data

    def update_status(
        self,
        id: UUID,
        processing_status: Literal['uploaded', 'queued', 'processing', 'completed', 'failed'],
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Change the processing status of an audio recording."""
        data: Dict[str, Any] = {"processing_status": processing_status}

        if error_message is not None:
            data["error_message"] = error_message

        result = (
            self.db.table(self.table_name)
            .update(data)
            .eq("id", str(id))
            .execute()
        )
        return result.data[0]