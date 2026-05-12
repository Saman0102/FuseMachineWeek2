"""
payment_crud.py - Database operations for payment records

Tracks payments made by customers. Payments are identified by 
customer and check number, so we treat them as a compound key.
"""

from sqlalchemy.orm import Session

from app import models
from app.schema.payment_schema import PaymentCreate, PaymentUpdate
from app.api_error_helpers import commit_or_raise, invalid_fk, not_found
import logging

logger = logging.getLogger(__name__)



def _get_payment(db: Session, customer_number: int, check_number: str):
    """Helper - find a specific payment by customer and check."""
    payment = db.query(models.Payment).filter(models.Payment.customerNumber == customer_number, models.Payment.checkNumber == check_number).first()
    if not payment:
        raise not_found("Payment", f"{customer_number}/{check_number}")
    return payment


def get_payments(db: Session, skip: int = 0, limit: int = 10):
    """Page through all payments."""
    logger.info("GET /payments")
    return db.query(models.Payment).order_by(models.Payment.customerNumber, models.Payment.checkNumber).offset(skip).limit(limit).all()


def get_payment(db: Session, customer_number: int, check_number: str):
    """Fetch a specific payment record."""
    logger.info("GET /payments/%s/%s", customer_number, check_number)
    return _get_payment(db, customer_number, check_number)


def get_payments_by_customer(db: Session, customer_number: int):
    """Get all payments from a customer, ordered most recent first."""
    logger.info("GET /payments/customer/%s", customer_number)
    if not db.query(models.Customer).filter(models.Customer.customerNumber == customer_number).first():
        raise not_found("Customer", customer_number)
    return db.query(models.Payment).filter(models.Payment.customerNumber == customer_number).order_by(models.Payment.paymentDate.desc()).all()


def create_payment(db: Session, data: PaymentCreate):
    """Record a new payment. Customer must exist."""
    logger.info("POST /payments %s/%s", data.customerNumber, data.checkNumber)
    if not db.query(models.Customer).filter(models.Customer.customerNumber == data.customerNumber).first():
        raise invalid_fk("customerNumber", data.customerNumber)
    payment = models.Payment(**data.model_dump())
    db.add(payment)
    commit_or_raise(db, fk_message="Invalid customerNumber", conflict_message=f"Payment {data.customerNumber}/{data.checkNumber} already exists")
    db.refresh(payment)
    return payment


def update_payment(db: Session, customer_number: int, check_number: str, data: PaymentUpdate):
    """Update a payment record."""
    logger.info("PUT /payments/%s/%s", customer_number, check_number)
    payment = _get_payment(db, customer_number, check_number)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)
    commit_or_raise(db)
    db.refresh(payment)
    return payment


def delete_payment(db: Session, customer_number: int, check_number: str):
    """Remove a payment record."""
    logger.info("DELETE /payments/%s/%s", customer_number, check_number)
    payment = _get_payment(db, customer_number, check_number)
    db.delete(payment)
    commit_or_raise(db)
    return True