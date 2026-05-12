"""
order_crud.py - Database operations for orders

Handles creation, retrieval, updates, and deletion of orders.
Makes sure orders belong to real customers and don't have orphaned details.
"""

from sqlalchemy.orm import Session, joinedload

from app import models
from app.schema.order_schema import OrderCreate, OrderUpdate
from app.api_error_helpers import commit_or_raise, conflict, invalid_fk, not_found
import logging

logger = logging.getLogger(__name__)


def _get_order(db: Session, order_number: int):
    """Helper - grab an order with its line items."""
    order = db.query(models.Order).options(joinedload(models.Order.order_details)).filter(models.Order.orderNumber == order_number).first()
    if not order:
        raise not_found("Order", order_number)
    return order


def get_orders(db: Session, skip: int = 0, limit: int = 10):
    """Page through orders."""
    logger.info("GET /orders")
    return db.query(models.Order).order_by(models.Order.orderNumber).offset(skip).limit(limit).all()


def get_order(db: Session, order_number: int):
    """Fetch one order with all its line items."""
    logger.info("GET /orders/%s", order_number)
    return _get_order(db, order_number)


def get_orders_with_orderdetails(db: Session, order_number: int):
    """Get an order with all its line items."""
    logger.info("GET /orders/%s/orderdetails", order_number)
    return _get_order(db, order_number)


def get_orders_by_customer(db: Session, customer_number: int):
    """Find all orders from a specific customer."""
    logger.info("GET /orders/customer/%s", customer_number)
    if not db.query(models.Customer).filter(models.Customer.customerNumber == customer_number).first():
        raise not_found("Customer", customer_number)
    return db.query(models.Order).filter(models.Order.customerNumber == customer_number).order_by(models.Order.orderNumber).all()


def create_order(db: Session, data: OrderCreate):
    """Create a new order. Customer must exist first."""
    logger.info("POST /orders %s", data.orderNumber)
    if not db.query(models.Customer).filter(models.Customer.customerNumber == data.customerNumber).first():
        raise invalid_fk("customerNumber", data.customerNumber)
    order = models.Order(**data.model_dump())
    db.add(order)
    commit_or_raise(db, fk_message="Invalid customerNumber", conflict_message=f"Order {data.orderNumber} already exists")
    db.refresh(order)
    return order


def update_order(db: Session, order_number: int, data: OrderUpdate):
    """Change an order's details. Verify customer if being changed."""
    logger.info("PUT /orders/%s", order_number)
    order = _get_order(db, order_number)
    updates = data.model_dump(exclude_unset=True)
    if "customerNumber" in updates and updates["customerNumber"] is not None and not db.query(models.Customer).filter(models.Customer.customerNumber == updates["customerNumber"]).first():
        raise invalid_fk("customerNumber", updates["customerNumber"])
    for field, value in updates.items():
        setattr(order, field, value)
    commit_or_raise(db, fk_message="Invalid customerNumber")
    db.refresh(order)
    return order


def delete_order(db: Session, order_number: int):
    """Remove an order - but only if it has no line items."""
    logger.info("DELETE /orders/%s", order_number)
    order = _get_order(db, order_number)
    if db.query(models.OrderDetail).filter(models.OrderDetail.orderNumber == order_number).first():
        raise conflict("Order has related order details")
    db.delete(order)
    commit_or_raise(db)
    return True