from pydantic import BaseModel, EmailStr, ConfigDict, Field


class EmployeeResponse(BaseModel):
    """Public employee information for Admin."""

    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    manager_id: int | None

    model_config = ConfigDict(from_attributes=True)

class AdminManagerDetailsResponse(BaseModel):
    """Manager information with team details."""

    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    total_employees: int
    employees: list[EmployeeResponse]

    model_config = ConfigDict(from_attributes=True)

class ManagerUpdate(BaseModel):
    """Fields that Admin can update for a Manager."""

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

class AdminDashboardResponse(BaseModel):
    total_managers: int
    active_managers: int
    inactive_managers: int

    total_employees: int
    active_employees: int
    inactive_employees: int

    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int