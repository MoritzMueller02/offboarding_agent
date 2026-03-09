from typing import Optional, List, Dict, Literal, Any
from uuid import UUID
from supabase import Client


class SessionRepository:

    def __init__(self, db: Client):
        self.db = db
        self.table_name = "sessions"

    def create(
        self,
        employee_id: UUID,
        title: str,
        session_type: Optional[Literal['exit_interview', 'knowledge_transfer', 'skills_review', 'project_handover']] = None,
        description: Optional[str] = None,
        scheduled_at: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Create a new offboarding session."""
        data: Dict[str, Any] = {
            "employee_id": str(employee_id),
            "title": title,
        }

        if session_type is not None:
            data["session_type"] = session_type
        if description is not None:
            data["description"] = description
        if scheduled_at is not None:
            data["scheduled_at"] = scheduled_at
        if metadata is not None:
            data["metadata"] = metadata

        result = self.db.table(self.table_name).insert(data).execute()
        return result.data[0]

    def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        result = self.db.table(self.table_name).select("*").eq("id", str(id)).execute()

        if not result.data:
            return None

        return result.data[0]

    def list_by_employee(self, employee_id: UUID) -> List[Dict[str, Any]]:
        result = (
            self.db.table(self.table_name)
            .select("*")
            .eq("employee_id", str(employee_id))
            .execute()
        )
        return result.data

    def update_status(
        self,
        id: UUID,
        status: Literal['scheduled', 'in_progress', 'completed', 'cancelled'],
        progress_percentage: Optional[int] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the status and progress of a session."""
        data: Dict[str, Any] = {"status": status}

        if progress_percentage is not None:
            data["progress_percentage"] = progress_percentage
        if started_at is not None:
            data["started_at"] = started_at
        if completed_at is not None:
            data["completed_at"] = completed_at

        result = (
            self.db.table(self.table_name)
            .update(data)
            .eq("id", str(id))
            .execute()
        )
        return result.data[0]
