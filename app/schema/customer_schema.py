from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import date
import logging

logger = logging.getLogger(__name__)


# ========================== Payment Schemas ==========================

class PaymentBase(BaseModel):
    checkNumber: str = Field(..., max_length=50, description="Unique check/payment reference")
    paymentDate: date = Field(..., description="Date the payment was made")
    amount: Decimal = Field(..., max_digits=10, decimal_places=2, description="Payment amount")


class PaymentOut(PaymentBase):
    """Returned when showing a customer's payments."""
    customerNumber: int

    model_config = {"from_attributes": True}


# ========================== Order Detail Schemas ==========================

class OrderDetailOut(BaseModel):
    """Single line item within an order."""
    productCode: str
    quantityOrdered: int
    priceEach: Decimal
    orderLineNumber: int

    model_config = {"from_attributes": True}


# ========================== Order Schemas ==========================

class OrderOut(BaseModel):
    """Returned when showing a customer's orders."""
    orderNumber: int
    orderDate: date
    requiredDate: date
    shippedDate: Optional[date] = None
    status: str
    comments: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderWithDetailsOut(OrderOut):
    """Order including its line-item details."""
    order_details: List[OrderDetailOut] = []


# ========================== Customer Schemas ==========================

class CustomerCreate(BaseModel):
    """
    Blueprint for *creating* a new customer.
    customerNumber is optional — the database can auto-assign it,
    but the seed data uses explicit IDs so we allow passing one.
    """
    customerNumber: Optional[int] = Field(None, description="Leave blank for auto-assignment")
    customerName: str = Field(..., min_length=1, max_length=50, description="Company / customer name")
    contactLastName: str = Field(..., min_length=1, max_length=50)
    contactFirstName: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=1, max_length=50)
    addressLine1: str = Field(..., min_length=1, max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    city: str = Field(..., min_length=1, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = Field(None, max_length=15)
    country: str = Field(..., min_length=1, max_length=50)
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Ensure phone contains only valid characters."""
        cleaned = v.replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "").replace(".", "")
        if not cleaned.isdigit():
            logger.warning("Validation error: invalid phone format — %s", v)
            raise ValueError("Phone must contain only digits, spaces, dashes, dots, parentheses, or +")
        return v


class CustomerUpdate(BaseModel):
    """
    Blueprint for *updating* a customer.
    All fields are optional — the user only sends what they want to change.
    """
    customerName: Optional[str] = Field(None, max_length=50)
    contactLastName: Optional[str] = Field(None, max_length=50)
    contactFirstName: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    addressLine1: Optional[str] = Field(None, max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = Field(None, max_length=15)
    country: Optional[str] = Field(None, max_length=50)
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)


class CustomerBase(BaseModel):
    """Core customer fields (without relations)."""
    customerNumber: int
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: str
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = None

    model_config = {"from_attributes": True}


class CustomerOut(CustomerBase):
    """
    Full customer view returned to the user,
    including related orders and payments.
    Empty lists are returned if no related data exists.
    """
    orders: List[OrderOut] = []
    payments: List[PaymentOut] = []

    model_config = {"from_attributes": True}