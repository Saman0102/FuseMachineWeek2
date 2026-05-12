from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


OrderStatus = Literal["Shipped", "Resolved", "Cancelled", "On Hold", "Disputed", "In Process"]


class OrderCreate(BaseModel):
    orderNumber: int
    orderDate: date
    requiredDate: date
    shippedDate: date | None = None
    status: OrderStatus
    comments: str | None = None
    customerNumber: int

    @model_validator(mode="after")
    def validate_dates(self):
        if self.requiredDate < self.orderDate:
            raise ValueError("requiredDate must be after orderDate")
        return self


class OrderUpdate(BaseModel):
    orderDate: date | None = None
    requiredDate: date | None = None
    shippedDate: date | None = None
    status: OrderStatus | None = None
    comments: str | None = None
    customerNumber: int | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.orderDate and self.requiredDate and self.requiredDate < self.orderDate:
            raise ValueError("requiredDate must be after orderDate")
        return self


class OrderDetailBaseOut(BaseModel):
    orderNumber: int
    productCode: str
    quantityOrdered: int
    priceEach: float
    orderLineNumber: int

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    orderNumber: int
    orderDate: date
    requiredDate: date
    shippedDate: date | None = None
    status: str
    comments: str | None = None
    customerNumber: int

    model_config = {"from_attributes": True}


class OrderWithDetailsOut(OrderOut):
    order_details: list[OrderDetailBaseOut] = []