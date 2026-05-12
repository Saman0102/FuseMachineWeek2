"""
payment_router.py - Payment API endpoints

Handles recording and managing customer payments. Can fetch by customer,
by individual check number, or list them all.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schema.payment_schema import PaymentCreate, PaymentOut, PaymentUpdate
from app.crud import payment_crud as crud

router = APIRouter(tags=["Payments"])


@router.get("/", response_model=list[PaymentOut])
def list_payments(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Page through all payments."""
    return crud.get_payments(db, skip=skip, limit=limit)


@router.get("/customer/{customerNumber}", response_model=list[PaymentOut])
def get_payments_by_customer(customerNumber: int, db: Session = Depends(get_db)):
    """Get all payments from a specific customer."""
    return crud.get_payments_by_customer(db, customerNumber)


@router.get("/{customerNumber}/{checkNumber}", response_model=PaymentOut)
def get_payment(customerNumber: int, checkNumber: str, db: Session = Depends(get_db)):
    """Fetch a specific payment."""
    return crud.get_payment(db, customerNumber, checkNumber)


@router.post("/", response_model=PaymentOut, status_code=201)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    """Record a new payment from a customer."""
    return crud.create_payment(db, data)


@router.put("/{customerNumber}/{checkNumber}", response_model=PaymentOut)
def update_payment(customerNumber: int, checkNumber: str, data: PaymentUpdate, db: Session = Depends(get_db)):
    """Update a payment record."""
    return crud.update_payment(db, customerNumber, checkNumber, data)


@router.delete("/{customerNumber}/{checkNumber}")
def delete_payment(customerNumber: int, checkNumber: str, db: Session = Depends(get_db)):
    """Remove a payment record."""
    crud.delete_payment(db, customerNumber, checkNumber)
    return {"detail": f"Payment {customerNumber}/{checkNumber} deleted successfully"}