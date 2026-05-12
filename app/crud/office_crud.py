"""
office_crud.py - Handle office location records

Manages all the company's office locations worldwide.
Not much validation needed here, just tracking locations and their employees.
"""

from sqlalchemy.orm import Session, joinedload
from app import models
from app.schema.office_schema import OfficeCreate, OfficeUpdate
from app.api_error_helpers import commit_or_raise, conflict, not_found
import logging

logger = logging.getLogger(__name__)



def _get_office(db: Session, office_code: str):
    """Helper - fetch an office with its employees."""
    office = db.query(models.Office).options(joinedload(models.Office.employees)).filter(models.Office.officeCode == office_code).first()
    if not office:
        raise not_found("Office", office_code)
    return office


def get_offices(db: Session, skip: int = 0, limit: int = 10):
    """Page through all offices."""
    logger.info("GET /offices")
    return db.query(models.Office).order_by(models.Office.officeCode).offset(skip).limit(limit).all()


def get_office(db: Session, office_code: str):
    """Look up a specific office."""
    logger.info("GET /offices/%s", office_code)
    return _get_office(db, office_code)


def get_offices_with_employees(db: Session, office_code: str):
    """Get an office and all its employees."""
    logger.info("GET /offices/%s/employees", office_code)
    return _get_office(db, office_code)


def create_office(db: Session, data: OfficeCreate):
    """Add a new office location."""
    logger.info("POST /offices %s", data.officeCode)
    office = models.Office(**data.model_dump())
    db.add(office)
    commit_or_raise(db, conflict_message=f"Office {data.officeCode} already exists")
    db.refresh(office)
    return office


def update_office(db: Session, office_code: str, data: OfficeUpdate):
    """Modify an office's details."""
    logger.info("PUT /offices/%s", office_code)
    office = _get_office(db, office_code)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(office, field, value)
    commit_or_raise(db)
    db.refresh(office)
    return office


def delete_office(db: Session, office_code: str):
    """Remove an office - but only if no one works there."""
    logger.info("DELETE /offices/%s", office_code)
    office = _get_office(db, office_code)
    if db.query(models.Employee).filter(models.Employee.officeCode == office_code).first():
        raise conflict("Office has employees assigned to it")
    db.delete(office)
    commit_or_raise(db)
    return True