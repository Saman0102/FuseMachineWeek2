"""
product_crud.py - All the database operations for products

This handles the boring stuff: retrieving products, adding new ones, 
updating them, and deleting when needed. Keeps it clean and separate 
from the API layer.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models
from app.schema.product_schema import ProductCreate, ProductUpdate
from app.api_error_helpers import commit_or_raise, invalid_fk, not_found, conflict
import logging

logger = logging.getLogger(__name__)



def _get_product(db: Session, product_code: str):
    """Internal helper - grabs a product by code and loads its order details."""
    product = (
        db.query(models.Product)
        .options(joinedload(models.Product.order_details))
        .filter(models.Product.productCode == product_code)
        .first()
    )
    if not product:
        raise not_found("Product", product_code)
    return product


def get_products(db: Session, skip: int = 0, limit: int = 10):
    """Get a page of products - useful for listing them all."""
    logger.info("GET /products skip=%s limit=%s", skip, limit)
    return (
        db.query(models.Product)
        .order_by(models.Product.productCode)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_product(db: Session, product_code: str):
    """Find a specific product by its code."""
    logger.info("GET /products/%s", product_code)
    return _get_product(db, product_code)


def get_products_with_orderdetails(db: Session, product_code: str):
    """Get a product with all its order details loaded."""
    logger.info("GET /products/%s/orderdetails", product_code)
    product = _get_product(db, product_code)
    return product


def create_product(db: Session, data: ProductCreate):
    """Add a new product to the catalog.
    
    First we check that the productLine actually exists - no point 
    creating a product for a product line that doesn't exist.
    """
    logger.info("POST /products %s", data.productCode)
    if not db.query(models.ProductLine).filter(models.ProductLine.productLine == data.productLine).first():
        raise invalid_fk("productLine", data.productLine)
    product = models.Product(**data.model_dump())
    db.add(product)
    commit_or_raise(db, fk_message="Invalid productLine", conflict_message=f"Product {data.productCode} already exists")
    db.refresh(product)
    return product


def update_product(db: Session, product_code: str, data: ProductUpdate):
    """Update a product's details.
    
    Only updates the fields that were actually provided. And again, 
    if they're changing the productLine, we verify it exists first.
    """
    logger.info("PUT /products/%s", product_code)
    product = _get_product(db, product_code)
    updates = data.model_dump(exclude_unset=True)
    if "productLine" in updates and not db.query(models.ProductLine).filter(models.ProductLine.productLine == updates["productLine"]).first():
        raise invalid_fk("productLine", updates["productLine"])
    for field, value in updates.items():
        setattr(product, field, value)
    commit_or_raise(db, fk_message="Invalid productLine")
    db.refresh(product)
    return product


def delete_product(db: Session, product_code: str):
    """Remove a product from the catalog.
    
    But only if nobody has ordered it yet. Don't want orphan order details.
    """
    logger.info("DELETE /products/%s", product_code)
    product = _get_product(db, product_code)
    if db.query(models.OrderDetail).filter(models.OrderDetail.productCode == product_code).first():
        raise conflict("Product has related order details")
    db.delete(product)
    commit_or_raise(db)
    return True