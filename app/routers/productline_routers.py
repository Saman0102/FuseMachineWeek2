"""
product_router.py - HTTP endpoints for managing the product catalog

Handles all the endpoints: listing, retrieving, creating, updating, and deleting products.
Each endpoint does minimal validation and delegates the actual work to the CRUD layer.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schema.product_schema import ProductCreate, ProductUpdate, ProductOut, ProductWithOrderDetailsOut
from app.crud import product_crud as crud
from app.api_error_helpers import not_found
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Products"])


@router.get("/", response_model=list[ProductOut])
def list_products(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get a page of products from the catalog."""
    logger.info("GET /products")
    return crud.get_products(db, skip=skip, limit=limit)


@router.get("/{productCode}", response_model=ProductOut)
def get_product(productCode: str, db: Session = Depends(get_db)):
    """Fetch a specific product by its code."""
    return crud.get_product(db, productCode)


@router.get("/{productCode}/orderdetails", response_model=ProductWithOrderDetailsOut)
def get_product_orderdetails(productCode: str, db: Session = Depends(get_db)):
    """See a product and all its line items from orders."""
    product = crud.get_products_with_orderdetails(db, productCode)
    return product


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Add a new product to the catalog."""
    try:
        return crud.create_product(db, data)
    except HTTPException:
        raise


@router.put("/{productCode}", response_model=ProductOut)
def update_product(productCode: str, data: ProductUpdate, db: Session = Depends(get_db)):
    """Update an existing product's info."""
    return crud.update_product(db, productCode, data)


@router.delete("/{productCode}")
def delete_product(productCode: str, db: Session = Depends(get_db)):
    """Remove a product from the catalog."""
    crud.delete_product(db, productCode)
    return {"detail": f"Product {productCode} deleted successfully"}