
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.schema.order_schema import OrderDetailBaseOut


class ProductCreate(BaseModel):
    productCode: str = Field(..., max_length=15)
    productName: str = Field(..., max_length=70)
    productLine: str = Field(..., max_length=50)
    productScale: str = Field(..., max_length=10)
    productVendor: str = Field(..., max_length=50)
    productDescription: str
    quantityInStock: int = Field(..., ge=0)
    buyPrice: Decimal = Field(..., max_digits=10, decimal_places=2)
    MSRP: Decimal = Field(..., max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def validate_prices(self):
        if self.MSRP < self.buyPrice:
            raise ValueError("MSRP must be greater than or equal to buyPrice")
        return self


class ProductUpdate(BaseModel):
    productName: str | None = Field(None, max_length=70)
    productLine: str | None = Field(None, max_length=50)
    productScale: str | None = Field(None, max_length=10)
    productVendor: str | None = Field(None, max_length=50)
    productDescription: str | None = None
    quantityInStock: int | None = Field(None, ge=0)
    buyPrice: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    MSRP: Decimal | None = Field(None, max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def validate_prices(self):
        if self.buyPrice is not None and self.MSRP is not None and self.MSRP < self.buyPrice:
            raise ValueError("MSRP must be greater than or equal to buyPrice")
        return self


class ProductOut(BaseModel):
    productCode: str
    productName: str
    productLine: str
    productScale: str
    productVendor: str
    productDescription: str
    quantityInStock: int
    buyPrice: Decimal
    MSRP: Decimal

    model_config = {"from_attributes": True}


class ProductWithOrderDetailsOut(ProductOut):
    order_details: list[OrderDetailBaseOut] = []