"""
productline_crud.py - Handle product categories/lines

Product lines are just groupings of related products (e.g., Cars, Motorcycles, etc).
They're simple but we need to make sure we don't delete one that has products.
"""

from sqlalchemy.orm import Session, joinedload

from app import models
from app.schema.productline_schema import ProductLineCreate, ProductLineUpdate
from app.api_error_helpers import commit_or_raise, invalid_fk, not_found, conflict
import logging

logger = logging.getLogger(__name__)



def _get_productline(db: Session, product_line: str):
    """Helper - fetch a product line with all its products."""
    productline = (
        db.query(models.ProductLine)
        .options(joinedload(models.ProductLine.products))
        .filter(models.ProductLine.productLine == product_line)
        .first()
    )
    if not productline:
        raise not_found("ProductLine", product_line)
    return productline


def get_productlines(db: Session, skip: int = 0, limit: int = 10):
    """Page through all product categories."""
    logger.info("GET /productlines")
    return db.query(models.ProductLine).order_by(models.ProductLine.productLine).offset(skip).limit(limit).all()


def get_productline(db: Session, product_line: str):
    """Look up a specific product category."""
    logger.info("GET /productlines/%s", product_line)
    return _get_productline(db, product_line)


def get_productlines_with_products(db: Session, product_line: str):
    """Get a product line and all its products."""
    logger.info("GET /productlines/%s/products", product_line)
    return _get_productline(db, product_line)


def create_productline(db: Session, data: ProductLineCreate):
    """Create a new product category."""
    logger.info("POST /productlines %s", data.productLine)
    productline = models.ProductLine(**data.model_dump())
    db.add(productline)
    commit_or_raise(db, conflict_message=f"ProductLine {data.productLine} already exists")
    db.refresh(productline)
    return productline


def update_productline(db: Session, product_line: str, data: ProductLineUpdate):
    """Update a product line's information."""
    logger.info("PUT /productlines/%s", product_line)
    productline = _get_productline(db, product_line)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(productline, field, value)
    commit_or_raise(db)
    db.refresh(productline)
    return productline


def delete_productline(db: Session, product_line: str):
    """Remove a product category - but only if it has no products in it."""
    logger.info("DELETE /productlines/%s", product_line)
    productline = _get_productline(db, product_line)
    if db.query(models.Product).filter(models.Product.productLine == product_line).first():
        raise conflict("Product line is still referenced by products")
    db.delete(productline)
    commit_or_raise(db)
    return True