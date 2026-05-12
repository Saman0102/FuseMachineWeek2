"""
orderdetail_crud.py - Handle individual line items in orders

Order details are the individual items/rows within an order.
Each line item references both an order and a product.
"""

from sqlalchemy.orm import Session

from app import models
from app.schema.orderdetail_schema import OrderDetailCreate, OrderDetailUpdate
from app.api_error_helpers import commit_or_raise, conflict, invalid_fk, not_found
import logging

logger = logging.getLogger(__name__)


def _get_orderdetail(db: Session, order_number: int, product_code: str):
    """Helper - find a specific line item by order and product."""
    detail = db.query(models.OrderDetail).filter(models.OrderDetail.orderNumber == order_number, models.OrderDetail.productCode == product_code).first()
    if not detail:
        raise not_found("OrderDetail", f"{order_number}/{product_code}")
    return detail


def get_orderdetails(db: Session, skip: int = 0, limit: int = 10):
    """Page through all order line items."""
    logger.info("GET /orderdetails")
    return db.query(models.OrderDetail).order_by(models.OrderDetail.orderNumber, models.OrderDetail.orderLineNumber).offset(skip).limit(limit).all()


def get_orderdetail(db: Session, order_number: int, product_code: str):
    """Fetch a specific line item from an order."""
    logger.info("GET /orderdetails/%s/%s", order_number, product_code)
    return _get_orderdetail(db, order_number, product_code)


def get_orderdetails_by_order(db: Session, order_number: int):
    """Get all line items in an order."""
    logger.info("GET /orderdetails/order/%s", order_number)
    if not db.query(models.Order).filter(models.Order.orderNumber == order_number).first():
        raise not_found("Order", order_number)
    return db.query(models.OrderDetail).filter(models.OrderDetail.orderNumber == order_number).order_by(models.OrderDetail.orderLineNumber).all()


def get_orderdetails_by_product(db: Session, product_code: str):
    """Find all orders that include a specific product."""
    logger.info("GET /orderdetails/product/%s", product_code)
    if not db.query(models.Product).filter(models.Product.productCode == product_code).first():
        raise not_found("Product", product_code)
    return db.query(models.OrderDetail).filter(models.OrderDetail.productCode == product_code).order_by(models.OrderDetail.orderNumber).all()


def create_orderdetail(db: Session, data: OrderDetailCreate):
    """Add a line item to an order. Both order and product must exist."""
    logger.info("POST /orderdetails %s/%s", data.orderNumber, data.productCode)
    if not db.query(models.Order).filter(models.Order.orderNumber == data.orderNumber).first():
        raise invalid_fk("orderNumber", data.orderNumber)
    if not db.query(models.Product).filter(models.Product.productCode == data.productCode).first():
        raise invalid_fk("productCode", data.productCode)
    detail = models.OrderDetail(**data.model_dump())
    db.add(detail)
    commit_or_raise(db, fk_message="Invalid orderNumber or productCode", conflict_message=f"OrderDetail {data.orderNumber}/{data.productCode} already exists")
    db.refresh(detail)
    return detail


def update_orderdetail(db: Session, order_number: int, product_code: str, data: OrderDetailUpdate):
    """Update a line item in an order."""
    logger.info("PUT /orderdetails/%s/%s", order_number, product_code)
    detail = _get_orderdetail(db, order_number, product_code)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(detail, field, value)
    commit_or_raise(db)
    db.refresh(detail)
    return detail


def delete_orderdetail(db: Session, order_number: int, product_code: str):
    """Remove a line item from an order."""
    logger.info("DELETE /orderdetails/%s/%s", order_number, product_code)
    detail = _get_orderdetail(db, order_number, product_code)
    db.delete(detail)
    commit_or_raise(db)
    return True