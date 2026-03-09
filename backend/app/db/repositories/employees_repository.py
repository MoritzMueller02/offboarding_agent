from typing import Optional, List, Dict, Literal, Any
from uuid import UUID
from supabase import Client


class EmployeeRepository:

    def __init__(self, db: Client):
        self.db = db
        self.table_name = "employees"

    def create(
        self,
        email: str,
        first_name: str,
        last_name: str,
        department: Optional[str] = None,
        position: Optional[str] = None,
        employee_id: Optional[str] = None,
        employment_status: Literal['active', 'offboarding', 'offboarded', 'archived'] = 'active',
        auth_user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Create a new employee record."""
        data: Dict[str, Any] = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "employment_status": employment_status,
        }

        if department is not None:
            data["department"] = department
        if position is not None:
            data["position"] = position
        if employee_id is not None:
            data["employee_id"] = employee_id
        if auth_user_id is not None:
            data["auth_user_id"] = str(auth_user_id)

        result = self.db.table(self.table_name).insert(data).execute()
        return result.data[0]

    def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        result = self.db.table(self.table_name).select("*").eq("id", str(id)).execute()

        if not result.data:
            return None

        return result.data[0]

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        result = self.db.table(self.table_name).select("*").eq("email", email).limit(1).execute()

        if not result.data:
            return None

        return result.data[0]

    def list_by_status(
        self,
        employment_status: Literal['active', 'offboarding', 'offboarded', 'archived'],
    ) -> List[Dict[str, Any]]:
        result = (
            self.db.table(self.table_name)
            .select("*")
            .eq("employment_status", employment_status)
            .execute()
        )
        return result.data

    def update_status(
        self,
        id: UUID,
        employment_status: Literal['active', 'offboarding', 'offboarded', 'archived'],
        offboarding_date: Optional[str] = None,
        last_working_day: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the employment status of an employee."""
        data: Dict[str, Any] = {"employment_status": employment_status}

        if offboarding_date is not None:
            data["offboarding_date"] = offboarding_date
        if last_working_day is not None:
            data["last_working_day"] = last_working_day

        result = (
            self.db.table(self.table_name)
            .update(data)
            .eq("id", str(id))
            .execute()
        )
        return result.data[0]
