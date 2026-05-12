

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schema.office_schema import OfficeCreate, OfficeOut, OfficeUpdate, OfficeWithEmployeesOut
from app.crud import office_crud as crud

router = APIRouter(tags=["Offices"])


@router.get("/", response_model=list[OfficeOut])
def list_offices(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Page through all office locations."""
    return crud.get_offices(db, skip=skip, limit=limit)


@router.get("/{officeCode}", response_model=OfficeOut)
def get_office(officeCode: str, db: Session = Depends(get_db)):
    """Get details about a specific office."""
    return crud.get_office(db, officeCode)


@router.get("/{officeCode}/employees", response_model=OfficeWithEmployeesOut)
def get_office_employees(officeCode: str, db: Session = Depends(get_db)):
    """See all employees at a specific office."""
    return crud.get_offices_with_employees(db, officeCode)


@router.post("/", response_model=OfficeOut, status_code=201)
def create_office(data: OfficeCreate, db: Session = Depends(get_db)):
    """Open a new office location."""
    return crud.create_office(db, data)


@router.put("/{officeCode}", response_model=OfficeOut)
def update_office(officeCode: str, data: OfficeUpdate, db: Session = Depends(get_db)):
    """Update an office's details."""
    return crud.update_office(db, officeCode, data)


@router.delete("/{officeCode}")
def delete_office(officeCode: str, db: Session = Depends(get_db)):
    """Close an office location."""
    crud.delete_office(db, officeCode)
    return {"detail": f"Office {officeCode} deleted successfully"}