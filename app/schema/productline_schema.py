
from pydantic import BaseModel, Field

from app.schema.product_schema import ProductOut


class ProductLineCreate(BaseModel):
    productLine: str = Field(..., max_length=50)
    textDescription: str | None = Field(None, max_length=4000)
    htmlDescription: str | None = None


class ProductLineUpdate(BaseModel):
    textDescription: str | None = Field(None, max_length=4000)
    htmlDescription: str | None = None


class ProductLineOut(BaseModel):
    productLine: str
    textDescription: str | None = None
    htmlDescription: str | None = None

    model_config = {"from_attributes": True}


class ProductLineWithProductsOut(ProductLineOut):
    products: list[ProductOut] = []