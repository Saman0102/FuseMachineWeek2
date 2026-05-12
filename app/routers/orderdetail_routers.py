"""
orderdetail_router.py - Order line item API endpoints

Handle individual line items within orders.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schema.orderdetail_schema import OrderDetailCreate, OrderDetailOut, OrderDetailUpdate
from app.crud import orderdetail_crud as crud

router = APIRouter(tags=["OrderDetails"])


@router.get("/", response_model=list[OrderDetailOut])
def list_orderdetails(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Page through all order line items."""
    return crud.get_orderdetails(db, skip=skip, limit=limit)


@router.get("/order/{orderNumber}", response_model=list[OrderDetailOut])
def get_orderdetails_by_order(orderNumber: int, db: Session = Depends(get_db)):
    """Get all line items in an order."""
    return crud.get_orderdetails_by_order(db, orderNumber)


@router.get("/product/{productCode}", response_model=list[OrderDetailOut])
def get_orderdetails_by_product(productCode: str, db: Session = Depends(get_db)):
    """Find all orders that include a specific product."""
    return crud.get_orderdetails_by_product(db, productCode)


@router.get("/{orderNumber}/{productCode}", response_model=OrderDetailOut)
def get_orderdetail(orderNumber: int, productCode: str, db: Session = Depends(get_db)):
    """Fetch a specific line item."""
    return crud.get_orderdetail(db, orderNumber, productCode)


@router.post("/", response_model=OrderDetailOut, status_code=201)
def create_orderdetail(data: OrderDetailCreate, db: Session = Depends(get_db)):
    """Add a line item to an order."""
    return crud.create_orderdetail(db, data)


@router.put("/{orderNumber}/{productCode}", response_model=OrderDetailOut)
def update_orderdetail(orderNumber: int, productCode: str, data: OrderDetailUpdate, db: Session = Depends(get_db)):
    """Update a line item."""
    return crud.update_orderdetail(db, orderNumber, productCode, data)


@router.delete("/{orderNumber}/{productCode}")
def delete_orderdetail(orderNumber: int, productCode: str, db: Session = Depends(get_db)):
    """Remove a line item from an order."""
    crud.delete_orderdetail(db, orderNumber, productCode)
    return {"detail": f"OrderDetail {orderNumber}/{productCode} deleted successfully"}