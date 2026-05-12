from pydantic import BaseModel, Field


class OfficeCreate(BaseModel):
    officeCode: str = Field(..., max_length=10)
    city: str = Field(..., max_length=50)
    phone: str = Field(..., max_length=50)
    addressLine1: str = Field(..., max_length=50)
    addressLine2: str | None = Field(None, max_length=50)
    state: str | None = Field(None, max_length=50)
    country: str = Field(..., max_length=50)
    postalCode: str = Field(..., max_length=15)
    territory: str = Field(..., max_length=10)


class OfficeUpdate(BaseModel):
    city: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=50)
    addressLine1: str | None = Field(None, max_length=50)
    addressLine2: str | None = Field(None, max_length=50)
    state: str | None = Field(None, max_length=50)
    country: str | None = Field(None, max_length=50)
    postalCode: str | None = Field(None, max_length=15)
    territory: str | None = Field(None, max_length=10)


class EmployeeBaseOut(BaseModel):
    employeeNumber: int
    lastName: str
    firstName: str
    extension: str
    email: str
    officeCode: str
    reportsTo: int | None = None
    jobTitle: str

    model_config = {"from_attributes": True}


class OfficeOut(BaseModel):
    officeCode: str
    city: str
    phone: str
    addressLine1: str
    addressLine2: str | None = None
    state: str | None = None
    country: str
    postalCode: str
    territory: str

    model_config = {"from_attributes": True}


class OfficeWithEmployeesOut(OfficeOut):
    employees: list[EmployeeBaseOut] = []