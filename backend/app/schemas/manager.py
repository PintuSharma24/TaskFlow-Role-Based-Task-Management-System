
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ManagerCreate(BaseModel):
    """Data required to create a Manager."""

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class ManagerResponse(BaseModel):
    """Public Manager information."""

    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class EmployeeCreate(BaseModel):
    """Data required to create an Employee."""

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


class EmployeeResponse(BaseModel):
    """Public Employee information."""

    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    manager_id: int | None

    model_config = ConfigDict(from_attributes=True)


class EmployeeUpdate(BaseModel):
    """Fields that Manager can update for an Employee."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: EmailStr | None = None

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128
    )

    is_active: bool | None = None