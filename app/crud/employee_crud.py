"""
employee_crud.py - Handle all employee-related database operations

Manages employees, their reporting structure, and customer assignments.
Mostly straightforward CRUD stuff, but we need to validate office codes 
and manager relationships.
"""

from sqlalchemy.orm import Session, joinedload

from app import models
from app.schema.employee_schema import EmployeeCreate, EmployeeUpdate
from app.api_error_helpers import commit_or_raise, conflict, invalid_fk, not_found
import logging

logger = logging.getLogger(__name__)



def _get_employee(db: Session, employee_number: int):
    """Helper - grab an employee with all their relationships loaded."""
    employee = db.query(models.Employee).options(joinedload(models.Employee.customers), joinedload(models.Employee.manager), joinedload(models.Employee.subordinates)).filter(models.Employee.employeeNumber == employee_number).first()
    if not employee:
        raise not_found("Employee", employee_number)
    return employee


def get_employees(db: Session, skip: int = 0, limit: int = 10):
    """Page through all employees."""
    logger.info("GET /employees")
    return db.query(models.Employee).order_by(models.Employee.employeeNumber).offset(skip).limit(limit).all()


def get_employee(db: Session, employee_number: int):
    """Look up one employee and all their relationships."""
    logger.info("GET /employees/%s", employee_number)
    return _get_employee(db, employee_number)


def get_employees_with_customers(db: Session, employee_number: int):
    """Get an employee with their customer list."""
    logger.info("GET /employees/%s/customers", employee_number)
    return _get_employee(db, employee_number)


def get_employees_with_reports(db: Session, employee_number: int):
    """Find all employees who report to this person."""
    logger.info("GET /employees/%s/reports", employee_number)
    _get_employee(db, employee_number)
    return db.query(models.Employee).filter(models.Employee.reportsTo == employee_number).order_by(models.Employee.employeeNumber).all()


def create_employee(db: Session, data: EmployeeCreate):
    """Add a new employee. They must belong to an existing office and (if set) report to an existing manager."""
    logger.info("POST /employees %s", data.employeeNumber)
    if not db.query(models.Office).filter(models.Office.officeCode == data.officeCode).first():
        raise invalid_fk("officeCode", data.officeCode)
    if data.reportsTo is not None and not db.query(models.Employee).filter(models.Employee.employeeNumber == data.reportsTo).first():
        raise invalid_fk("reportsTo", data.reportsTo)
    employee = models.Employee(**data.model_dump())
    db.add(employee)
    commit_or_raise(db, fk_message="Invalid officeCode or reportsTo", conflict_message=f"Employee {data.employeeNumber} already exists")
    db.refresh(employee)
    return employee


def update_employee(db: Session, employee_number: int, data: EmployeeUpdate):
    """Modify an employee's details. Validate office and manager if changed."""
    logger.info("PUT /employees/%s", employee_number)
    employee = _get_employee(db, employee_number)
    updates = data.model_dump(exclude_unset=True)
    if "officeCode" in updates and not db.query(models.Office).filter(models.Office.officeCode == updates["officeCode"]).first():
        raise invalid_fk("officeCode", updates["officeCode"])
    if "reportsTo" in updates and updates["reportsTo"] is not None and not db.query(models.Employee).filter(models.Employee.employeeNumber == updates["reportsTo"]).first():
        raise invalid_fk("reportsTo", updates["reportsTo"])
    for field, value in updates.items():
        setattr(employee, field, value)
    commit_or_raise(db, fk_message="Invalid officeCode or reportsTo")
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee_number: int):
    """Remove an employee - but only if they have no reports and aren't a sales rep."""
    logger.info("DELETE /employees/%s", employee_number)
    employee = _get_employee(db, employee_number)
    if db.query(models.Employee).filter(models.Employee.reportsTo == employee_number).first():
        raise conflict("Employee has direct reports")
    if db.query(models.Customer).filter(models.Customer.salesRepEmployeeNumber == employee_number).first():
        raise conflict("Employee is assigned to customers")
    db.delete(employee)
    commit_or_raise(db)
    return True