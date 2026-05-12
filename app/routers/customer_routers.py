from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import crud
from app.schema.customer_schema import (
    CustomerBase,
    CustomerOut,
    CustomerCreate,
    CustomerUpdate,
    OrderOut,
    PaymentOut
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    responses={404: {"description": "Customer not found"}},
)


@router.get("/", response_model=List[CustomerBase], summary="List all customers")
def list_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return (1–100)"),
    db: Session = Depends(get_db),
):
    """Get a page of customers."""
    logger.info("GET /customers — skip=%d, limit=%d", skip, limit)
    customers = crud.get_customers(db, skip=skip, limit=limit)
    logger.info("Response: returning %d customers", len(customers))
    return customers


@router.get(
    "/{customer_number}",
    response_model=CustomerOut,
    summary="Get a specific customer with orders & payments",
)
def get_customer(customer_number: int, db: Session = Depends(get_db)):
    """Fetch a customer and all their orders and payments."""
    logger.info("GET /customers/%d", customer_number)
    customer = crud.get_customer(db, customer_number)
    if not customer:
        logger.error("Endpoint 404: Customer ID %d not found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer {customer_number} not found")
    logger.info("Response: returning customer %s (ID: %d)", customer.customerName, customer_number)
    return customer


@router.get(
    "/{customer_number}/orders",
    response_model=List[OrderOut],
    summary="Get all orders for a customer",
)
def get_customer_orders(customer_number: int, db: Session = Depends(get_db)):
    """List all orders from a specific customer."""
    logger.info("GET /customers/%d/orders", customer_number)
    customer = crud.get_customer(db, customer_number)
    if not customer:
        logger.error("Endpoint 404: Customer ID %d not found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer {customer_number} not found")
    orders = crud.get_customer_orders(db, customer_number)
    logger.info("Response: returning %d orders for customer %d", len(orders), customer_number)
    return orders


@router.get(
    "/{customer_number}/payments",
    response_model=List[PaymentOut],
    summary="Get all payments for a customer",
)
def get_customer_payments(customer_number: int, db: Session = Depends(get_db)):
    """Get all payments a customer has made."""
    logger.info("GET /customers/%d/payments", customer_number)
    customer = crud.get_customer(db, customer_number)
    if not customer:
        logger.error("Endpoint 404: Customer ID %d not found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer {customer_number} not found")
    payments = crud.get_customer_payments(db, customer_number)
    logger.info("Response: returning %d payments for customer %d", len(payments), customer_number)
    return payments


@router.post("/", response_model=CustomerBase, status_code=201, summary="Create a new customer")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Add a new customer. Auto-assigns a customer ID if not provided."""
    logger.info("POST /customers — creating '%s'", customer.customerName)
    try:
        new_customer = crud.create_customer(db, customer)
    except Exception as e:
        logger.error("Failed to create customer: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Could not create customer: {str(e)}")
    logger.info("Response 201: customer created — ID %d", new_customer.customerNumber)
    return new_customer


@router.put(
    "/{customer_number}",
    response_model=CustomerBase,
    summary="Update an existing customer",
)
def update_customer(
    customer_number: int,
    update_data: CustomerUpdate,
    db: Session = Depends(get_db),
):
    """Update a customer's info. Only provided fields are changed."""
    logger.info("PUT /customers/%d", customer_number)
    updated = crud.update_customer(db, customer_number, update_data)
    if not updated:
        logger.error("Endpoint 404: Customer ID %d not found for update", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer {customer_number} not found")
    logger.info("Response: customer %d updated", customer_number)
    return updated


@router.delete(
    "/{customer_number}",
    status_code=200,
    summary="Delete a customer",
)
def delete_customer(customer_number: int, db: Session = Depends(get_db)):
    """Remove a customer and all their related data."""
    logger.info("DELETE /customers/%d", customer_number)
    deleted = crud.delete_customer(db, customer_number)
    if not deleted:
        logger.error("Endpoint 404: Customer ID %d not found for deletion", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer {customer_number} not found")
    logger.info("Response: customer %d deleted", customer_number)
    return {"detail": f"Customer {customer_number} deleted successfully"}