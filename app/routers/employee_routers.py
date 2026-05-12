"""
employee_router.py - Employee API endpoints

Handles all HTTP requests related to employees: listing, fetching,
creating, updating, and deleting. Also has endpoints to see who reports
to someone and which customers they manage.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schema.employee_schema import EmployeeCreate, EmployeeOut, EmployeeUpdate, EmployeeWithCustomersOut, EmployeeWithReportsOut
from app.crud import employee_crud as crud

router = APIRouter(tags=["Employees"])


@router.get("/", response_model=list[EmployeeOut])
def list_employees(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Page through all employees."""
    return crud.get_employees(db, skip=skip, limit=limit)


@router.get("/{employeeNumber}", response_model=EmployeeOut)
def get_employee(employeeNumber: int, db: Session = Depends(get_db)):
    """Get details about a specific employee."""
    return crud.get_employee(db, employeeNumber)


@router.get("/{employeeNumber}/customers", response_model=EmployeeWithCustomersOut)
def get_employee_customers(employeeNumber: int, db: Session = Depends(get_db)):
    """See which customers this employee manages."""
    return crud.get_employees_with_customers(db, employeeNumber)


@router.get("/{employeeNumber}/reports", response_model=list[EmployeeOut])
def get_employee_reports(employeeNumber: int, db: Session = Depends(get_db)):
    """Find all employees who report to this person."""
    return crud.get_employees_with_reports(db, employeeNumber)


@router.post("/", response_model=EmployeeOut, status_code=201)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db)):
    """Hire a new employee."""
    return crud.create_employee(db, data)


@router.put("/{employeeNumber}", response_model=EmployeeOut)
def update_employee(employeeNumber: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    """Update an employee's info."""
    return crud.update_employee(db, employeeNumber, data)


@router.delete("/{employeeNumber}")
def delete_employee(employeeNumber: int, db: Session = Depends(get_db)):
    """Remove an employee from the system."""
    crud.delete_employee(db, employeeNumber)
    return {"detail": f"Employee {employeeNumber} deleted successfully"}