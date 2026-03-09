from typing import Optional, List, Dict, Literal, Any
from uuid import UUID
from supabase import Client


class DocumentRepository:

    def __init__(self, db: Client):
        self.db = db
        self.table_name = "documents"

    def create(
        self,
        session_id: UUID,
        storage_path: str,
        file_name: str,
        storage_bucket: str = "documents",
        document_type: Optional[Literal['pdf', 'docx', 'txt', 'markdown', 'presentation', 'spreadsheet', 'other']] = None,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
        processing_status: Literal['uploaded', 'queued', 'extracting', 'completed', 'failed'] = 'uploaded',
    ) -> Dict[str, Any]:
        """Save document metadata to the database."""
        data: Dict[str, Any] = {
            "session_id": str(session_id),
            "storage_path": storage_path,
            "storage_bucket": storage_bucket,
            "file_name": file_name,
            "processing_status": processing_status,
        }

        if document_type is not None:
            data["document_type"] = document_type
        if mime_type is not None:
            data["mime_type"] = mime_type
        if file_size is not None:
            data["file_size"] = file_size

        result = self.db.table(self.table_name).insert(data).execute()
        return result.data[0]

    def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        result = self.db.table(self.table_name).select("*").eq("id", str(id)).execute()

        if not result.data:
            return None

        return result.data[0]

    def list_by_session(self, session_id: UUID) -> List[Dict[str, Any]]:
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
        processing_status: Literal['uploaded', 'queued', 'extracting', 'completed', 'failed'],
        extracted_text: Optional[str] = None,
        page_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the processing status of a document."""
        data: Dict[str, Any] = {"processing_status": processing_status}

        if extracted_text is not None:
            data["extracted_text"] = extracted_text
        if page_count is not None:
            data["page_count"] = page_count
        if error_message is not None:
            data["error_message"] = error_message

        result = (
            self.db.table(self.table_name)
            .update(data)
            .eq("id", str(id))
            .execute()
        )
        return result.data[0]
