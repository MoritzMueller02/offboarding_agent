from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.dependencies import get_db
from app.db.repositories.employees_repository import EmployeeRepository
from app.models.schema import Employee, EmployeeCreate

router = APIRouter()


class EmployeeStatusUpdate(BaseModel):
    employment_status: str
    offboarding_date: Optional[datetime] = None
    last_working_day: Optional[datetime] = None


@router.post("/", response_model=Employee, status_code=201)
def create_employee(payload: EmployeeCreate, db: Client = Depends(get_db)):
    """Create a new employee"""
    repo = EmployeeRepository(db)

    existing = repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Employee with this email already exists")

    return repo.create(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        department=payload.department,
        position=payload.position,
        employee_id=payload.employee_id,
        employment_status=payload.employment_status,
    )


@router.get("/status/{status}", response_model=List[Employee])
def list_by_status(status: str, db: Client = Depends(get_db)):
    """List all employees with a given employment status"""
    valid = ('active', 'offboarding', 'offboarded', 'archived')
    if status not in valid:
        raise HTTPException(status_code=422, detail=f"Invalid status. Must be one of: {valid}")

    return EmployeeRepository(db).list_by_status(status)


@router.get("/email/{email}", response_model=Employee)
def get_by_email(email: str, db: Client = Depends(get_db)):
    """Get an employee by email address"""
    repo = EmployeeRepository(db)
    employee = repo.get_by_email(email)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: UUID, db: Client = Depends(get_db)):
    """Get an employee by ID"""
    repo = EmployeeRepository(db)
    employee = repo.get_by_id(employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.patch("/{employee_id}/status", response_model=Employee)
def update_employee_status(
    employee_id: UUID,
    payload: EmployeeStatusUpdate,
    db: Client = Depends(get_db),
):
    """Update the employment status of an employee"""
    repo = EmployeeRepository(db)

    if not repo.get_by_id(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    return repo.update_status(
        id=employee_id,
        employment_status=payload.employment_status,
        offboarding_date=payload.offboarding_date.isoformat() if payload.offboarding_date else None,
        last_working_day=payload.last_working_day.isoformat() if payload.last_working_day else None,
    )
