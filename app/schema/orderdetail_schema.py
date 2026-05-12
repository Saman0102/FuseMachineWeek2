"""
orderdetail_schemas.py - Order detail validation models

Defines what order line item data looks valid and what we send back when
returning order line items.
"""

from decimal import Decimal

from pydantic import BaseModel, Field


class OrderDetailCreate(BaseModel):
    orderNumber: int
    productCode: str = Field(..., max_length=15)
    quantityOrdered: int = Field(..., gt=0)
    priceEach: Decimal = Field(..., max_digits=10, decimal_places=2)
    orderLineNumber: int = Field(..., ge=1, le=32767)


class OrderDetailUpdate(BaseModel):
    quantityOrdered: int | None = Field(None, gt=0)
    priceEach: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    orderLineNumber: int | None = Field(None, ge=1, le=32767)


class OrderDetailOut(BaseModel):
    orderNumber: int
    productCode: str
    quantityOrdered: int
    priceEach: Decimal
    orderLineNumber: int

    model_config = {"from_attributes": True}