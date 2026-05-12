
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class PaymentCreate(BaseModel):
    customerNumber: int
    checkNumber: str = Field(..., max_length=50)
    paymentDate: date
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def validate_date(self):
        if self.paymentDate > date.today():
            raise ValueError("paymentDate cannot be in the future")
        return self


class PaymentUpdate(BaseModel):
    paymentDate: date | None = None
    amount: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def validate_date(self):
        if self.paymentDate and self.paymentDate > date.today():
            raise ValueError("paymentDate cannot be in the future")
        return self


class PaymentOut(BaseModel):
    customerNumber: int
    checkNumber: str
    paymentDate: date
    amount: Decimal

    model_config = {"from_attributes": True}