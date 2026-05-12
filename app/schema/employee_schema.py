from pydantic import BaseModel, Field, EmailStr
from app.schema.customer_schema import CustomerBase


class EmployeeCreate(BaseModel):
    employeeNumber: int
    lastName: str = Field(..., max_length=50)
    firstName: str = Field(..., max_length=50)
    extension: str = Field(..., max_length=10)
    email: EmailStr
    officeCode: str = Field(..., max_length=10)
    reportsTo: int | None = None
    jobTitle: str = Field(..., max_length=50)


class EmployeeUpdate(BaseModel):
    lastName: str | None = Field(None, max_length=50)
    firstName: str | None = Field(None, max_length=50)
    extension: str | None = Field(None, max_length=10)
    email: EmailStr | None = None
    officeCode: str | None = Field(None, max_length=10)
    reportsTo: int | None = None
    jobTitle: str | None = Field(None, max_length=50)


class EmployeeOut(BaseModel):
    employeeNumber: int
    lastName: str
    firstName: str
    extension: str
    email: str
    officeCode: str
    reportsTo: int | None = None
    jobTitle: str

    model_config = {"from_attributes": True}


class EmployeeWithCustomersOut(EmployeeOut):
    customers: list[CustomerBase] = []


class EmployeeWithReportsOut(EmployeeOut):
    reports: list[EmployeeOut] = []