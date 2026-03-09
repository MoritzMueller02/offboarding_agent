from typing import Optional, List, Dict, Any
from uuid import UUID
from supabase import Client


class TranscriptionRepository:
    def __init__(self, db: Client):
        self.db = db
        self.table_name = "transcriptions"

    def create(
        self,
        audio_recording_id: UUID,
        text: str,
        model_name: Optional[str] = None,
        language: Optional[str] = None,
        confidence_score: Optional[float] = None,
        word_timestamps: Optional[dict] = None,
        processing_time_ms: Optional[int] = None,
    ) -> Dict[str, Any]:

        data: Dict[str, Any] = {
            "audio_recording_id": str(audio_recording_id),
            "text": text,
        }

        if language is not None:
            data["language"] = language
        if model_name is not None:
            data["model_name"] = model_name
        if confidence_score is not None:
            data["confidence_score"] = confidence_score
        if word_timestamps:
            data["word_timestamps"] = word_timestamps
        if processing_time_ms is not None:
            data["processing_time_ms"] = processing_time_ms

        result = self.db.table(self.table_name).insert(data).execute()
        return result.data[0]

    def get_by_id(self, transcription_id: UUID) -> Optional[Dict[str, Any]]:
        result = self.db.table(self.table_name).select("*").eq("id", str(transcription_id)).execute()

        if not result.data:
            return None

        return result.data[0]

    def get_by_audio_id(self, audio_recording_id: UUID) -> Optional[Dict[str, Any]]:
        result = (
            self.db.table(self.table_name)
            .select("*")
            .eq("audio_recording_id", str(audio_recording_id))
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        return result.data[0]
