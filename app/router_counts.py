from typing import Dict
import asyncio
from time import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Statistics"])

def _fetch_count_sync(count_func, table_name: str, db: Session) -> tuple:
    try:
        count = count_func(db)
        return (table_name, count)
    except Exception as e:
        logger.error("Error counting %s: %s", table_name, str(e))
        return (table_name, 0)


async def _gather_all_counts(db: Session) -> Dict[str, int]:
    logger.info("Starting concurrent count fetch")
    start = time.time()
    
    tasks = [
        asyncio.to_thread(_fetch_count_sync, crud.get_customers_count, "customers", db),
        asyncio.to_thread(_fetch_count_sync, crud.get_orders_count, "orders", db),
        asyncio.to_thread(_fetch_count_sync, crud.get_products_count, "products", db),
        asyncio.to_thread(_fetch_count_sync, crud.get_employees_count, "employees", db),
        asyncio.to_thread(_fetch_count_sync, crud.get_offices_count, "offices", db),
        asyncio.to_thread(_fetch_count_sync, crud.get_payments_count, "payments", db),
        asyncio.to_thread(_fetch_count_sync, crud.get_orderdetails_count, "orderdetails", db),
        asyncio.to_thread(_fetch_count_sync, crud.get_productlines_count, "productlines", db),
    ]
    
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    logger.info("Concurrent fetch completed in %.3f seconds", elapsed)
    
    return {table: count for table, count in results}


@router.get("/customers/count")
def get_customers_count(db: Session = Depends(get_db)):
    """How many customers do we have?"""
    logger.info("GET /customers/count")
    try:
        count = crud.get_customers_count(db)
        return {"table": "customers", "count": count}
    except Exception as e:
        logger.error("Error counting customers: %s", str(e))
        return {"table": "customers", "count": 0}


@router.get("/orders/count")
def get_orders_count(db: Session = Depends(get_db)):
    """How many orders exist?"""
    logger.info("GET /orders/count")
    try:
        count = crud.get_orders_count(db)
        return {"table": "orders", "count": count}
    except Exception as e:
        logger.error("Error counting orders: %s", str(e))
        return {"table": "orders", "count": 0}


@router.get("/products/count")
def get_products_count(db: Session = Depends(get_db)):
    """How many products in our catalog?"""
    logger.info("GET /products/count")
    try:
        count = crud.get_products_count(db)
        return {"table": "products", "count": count}
    except Exception as e:
        logger.error("Error counting products: %s", str(e))
        return {"table": "products", "count": 0}


@router.get("/employees/count")
def get_employees_count(db: Session = Depends(get_db)):
    """How many employees on the team?"""
    logger.info("GET /employees/count")
    try:
        count = crud.get_employees_count(db)
        return {"table": "employees", "count": count}
    except Exception as e:
        logger.error("Error counting employees: %s", str(e))
        return {"table": "employees", "count": 0}


@router.get("/offices/count")
def get_offices_count(db: Session = Depends(get_db)):
    """How many offices worldwide?"""
    logger.info("GET /offices/count")
    try:
        count = crud.get_offices_count(db)
        return {"table": "offices", "count": count}
    except Exception as e:
        logger.error("Error counting offices: %s", str(e))
        return {"table": "offices", "count": 0}


@router.get("/payments/count")
def get_payments_count(db: Session = Depends(get_db)):
    """How many payments recorded?"""
    logger.info("GET /payments/count")
    try:
        count = crud.get_payments_count(db)
        return {"table": "payments", "count": count}
    except Exception as e:
        logger.error("Error counting payments: %s", str(e))
        return {"table": "payments", "count": 0}


@router.get("/orderdetails/count")
def get_orderdetails_count(db: Session = Depends(get_db)):
    """How many line items across all orders?"""
    logger.info("GET /orderdetails/count")
    try:
        count = crud.get_orderdetails_count(db)
        return {"table": "orderdetails", "count": count}
    except Exception as e:
        logger.error("Error counting order details: %s", str(e))
        return {"table": "orderdetails", "count": 0}


@router.get("/productlines/count")
def get_productlines_count(db: Session = Depends(get_db)):
    """How many product categories?"""
    logger.info("GET /productlines/count")
    try:
        count = crud.get_productlines_count(db)
        return {"table": "productlines", "count": count}
    except Exception as e:
        logger.error("Error counting product lines: %s", str(e))
        return {"table": "productlines", "count": 0}
        return {"table": "orderdetails", "count": 0}


@router.get("/productlines/count")
def get_productlines_count(db: Session = Depends(get_db)):
    logger.info("GET /productlines/count")
    try:
        count = crud.get_productlines_count(db)
        return {"table": "productlines", "count": count}
    except Exception as e:
        logger.error("Error: %s", str(e))
        return {"table": "productlines", "count": 0}




@router.get("/overall_counts")
async def get_overall_counts(db: Session = Depends(get_db)):
    logger.info("GET /overall_counts")
    try:
        aggregated = await _gather_all_counts(db)
        return aggregated
    except Exception as e:
        logger.error("Error in /overall_counts: %s", str(e))
        return {
            "customers": 0,
            "orders": 0,
            "products": 0,
            "employees": 0,
            "offices": 0,
            "payments": 0,
            "orderdetails": 0,
            "productlines": 0,
        }