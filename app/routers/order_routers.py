

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schema.order_schema import OrderCreate, OrderOut, OrderUpdate, OrderWithDetailsOut
from app.crud import order_crud as crud

router = APIRouter(tags=["Orders"])


@router.get("/", response_model=list[OrderOut])
def list_orders(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get a page of orders."""
    return crud.get_orders(db, skip=skip, limit=limit)


@router.get("/{orderNumber}", response_model=OrderOut)
def get_order(orderNumber: int, db: Session = Depends(get_db)):
    """Fetch a specific order."""
    return crud.get_order(db, orderNumber)


@router.get("/{orderNumber}/orderdetails", response_model=OrderWithDetailsOut)
def get_order_details(orderNumber: int, db: Session = Depends(get_db)):
    """Get an order with all its line items."""
    return crud.get_orders_with_orderdetails(db, orderNumber)


@router.get("/customer/{customerNumber}", response_model=list[OrderOut])
def get_orders_by_customer(customerNumber: int, db: Session = Depends(get_db)):
    """Get all orders from a specific customer."""
    return crud.get_orders_by_customer(db, customerNumber)


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order."""
    return crud.create_order(db, data)


@router.put("/{orderNumber}", response_model=OrderOut)
def update_order(orderNumber: int, data: OrderUpdate, db: Session = Depends(get_db)):
    """Modify an order's details."""
    return crud.update_order(db, orderNumber, data)


@router.delete("/{orderNumber}")
def delete_order(orderNumber: int, db: Session = Depends(get_db)):
    """Remove an order."""
    crud.delete_order(db, orderNumber)
    return {"detail": f"Order {orderNumber} deleted successfully"}