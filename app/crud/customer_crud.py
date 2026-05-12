"""
crud.py — The Kitchen (Database Operations)
=============================================
CRUD = Create, Read, Update, Delete.
This layer talks ONLY to the database — never to the internet.
All queries are written using SQLAlchemy ORM.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List

from app.models import (
    Customer, Order, Payment, Product, Employee, Office, 
    OrderDetail, ProductLine
)
from app.schema.customer_schema import CustomerCreate, CustomerUpdate
import logging

logger = logging.getLogger(__name__)


# ========================== CREATE ==========================

def create_customer(db: Session, customer_data: CustomerCreate) -> Customer:
    """
    Insert a new customer into the database.
    If customerNumber is not provided, auto-assign the next available ID.
    """
    logger.info("Creating new customer: %s", customer_data.customerName)

    if customer_data.customerNumber is None:
        # Auto-assign: find the current max and add 1
        from sqlalchemy import func
        max_id = db.query(func.max(Customer.customerNumber)).scalar() or 0
        customer_data.customerNumber = max_id + 1
        logger.debug("Auto-assigned customerNumber: %d", customer_data.customerNumber)

    db_customer = Customer(**customer_data.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    logger.info("Customer created successfully — ID: %d", db_customer.customerNumber)
    return db_customer


# ========================== READ ==========================

def get_customer(db: Session, customer_number: int) -> Optional[Customer]:
    """
    Fetch a single customer by their customerNumber.
    Eagerly loads related orders and payments.
    """
    logger.info("Fetching customer ID: %d", customer_number)

    customer = (
        db.query(Customer)
        .options(
            joinedload(Customer.orders),
            joinedload(Customer.payments),
        )
        .filter(Customer.customerNumber == customer_number)
        .first()
    )

    if customer:
        logger.info("Customer found: %s (ID: %d)", customer.customerName, customer_number)
    else:
        logger.warning("Customer not found: ID %d", customer_number)

    return customer


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 10,
) -> List[Customer]:
    """
    Fetch a paginated list of customers.

    Parameters
    ----------
    skip  : number of records to pass over (offset).
    limit : maximum number of records to return.
    """
    logger.info("Listing customers — skip=%d, limit=%d", skip, limit)

    customers = (
        db.query(Customer)
        .order_by(Customer.customerNumber)
        .offset(skip)
        .limit(limit)
        .all()
    )

    logger.info("Returned %d customers", len(customers))
    return customers


def get_customer_orders(db: Session, customer_number: int) -> List[Order]:
    """Fetch all orders for a specific customer."""
    logger.info("Fetching orders for customer ID: %d", customer_number)

    orders = (
        db.query(Order)
        .filter(Order.customerNumber == customer_number)
        .order_by(Order.orderDate.desc())
        .all()
    )

    logger.info("Found %d orders for customer ID: %d", len(orders), customer_number)
    return orders


def get_customer_payments(db: Session, customer_number: int) -> List[Payment]:
    """Fetch all payments for a specific customer."""
    logger.info("Fetching payments for customer ID: %d", customer_number)

    payments = (
        db.query(Payment)
        .filter(Payment.customerNumber == customer_number)
        .order_by(Payment.paymentDate.desc())
        .all()
    )

    logger.info("Found %d payments for customer ID: %d", len(payments), customer_number)
    return payments


# ========================== UPDATE ==========================

def update_customer(
    db: Session,
    customer_number: int,
    update_data: CustomerUpdate,
) -> Optional[Customer]:
    """
    Update an existing customer. Only the provided (non-None) fields are changed.
    Returns the updated customer, or None if the customer doesn't exist.
    """
    logger.info("Updating customer ID: %d", customer_number)

    db_customer = db.query(Customer).filter(
        Customer.customerNumber == customer_number
    ).first()

    if not db_customer:
        logger.warning("Update failed — customer not found: ID %d", customer_number)
        return None

    # Only update fields that were explicitly set
    update_fields = update_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(db_customer, field, value)
        logger.debug("  Updated field '%s' for customer %d", field, customer_number)

    db.commit()
    db.refresh(db_customer)

    logger.info("Customer updated successfully — ID: %d", customer_number)
    return db_customer


# ========================== DELETE ==========================

def delete_customer(db: Session, customer_number: int) -> bool:
    """
    Delete a customer by their customerNumber.
    Returns True if deleted, False if the customer was not found.
    """
    logger.info("Deleting customer ID: %d", customer_number)

    db_customer = db.query(Customer).filter(
        Customer.customerNumber == customer_number
    ).first()

    if not db_customer:
        logger.warning("Delete failed — customer not found: ID %d", customer_number)
        return False

    db.delete(db_customer)
    db.commit()

    logger.info("Customer deleted successfully — ID: %d", customer_number)
    return True


def get_customers_count(db: Session) -> int:
    logger.info("Counting customers")
    try:
        count = db.query(func.count(Customer.customerNumber)).scalar() or 0
        return count
    except Exception as e:
        logger.error("Error counting customers: %s", str(e))
        return 0


def get_orders_count(db: Session) -> int:
    logger.info("Counting orders")
    try:
        count = db.query(func.count(Order.orderNumber)).scalar() or 0
        return count
    except Exception as e:
        logger.error("Error counting orders: %s", str(e))
        return 0


def get_products_count(db: Session) -> int:
    logger.info("Counting products")
    try:
        count = db.query(func.count(Product.productCode)).scalar() or 0
        return count
    except Exception as e:
        logger.error("Error counting products: %s", str(e))
        return 0


def get_employees_count(db: Session) -> int:
    logger.info("Counting employees")
    try:
        count = db.query(func.count(Employee.employeeNumber)).scalar() or 0
        return count
    except Exception as e:
        logger.error("Error counting employees: %s", str(e))
        return 0


def get_offices_count(db: Session) -> int:
    logger.info("Counting offices")
    try:
        count = db.query(func.count(Office.officeCode)).scalar() or 0
        return count
    except Exception as e:
        logger.error("Error counting offices: %s", str(e))
        return 0


def get_payments_count(db: Session) -> int:
    logger.info("Counting payments")
    try:
        count = db.query(func.count(Payment.checkNumber)).scalar() or 0
        return count
    except Exception as e:
        logger.error("Error counting payments: %s", str(e))
        return 0


def get_orderdetails_count(db: Session) -> int:
    logger.info("Counting order details")
    try:
        count = db.query(func.count(OrderDetail.orderNumber)).scalar() or 0
        return count
    except Exception as e:
        logger.error("Error counting order details: %s", str(e))
        return 0


def get_productlines_count(db: Session) -> int:
    logger.info("Counting product lines")
    try:
        count = db.query(func.count(ProductLine.productLine)).scalar() or 0
        return count
    except Exception as e:
        logger.error("Error counting product lines: %s", str(e))
        return 0