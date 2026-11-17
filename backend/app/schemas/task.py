from datetime import date

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import datetime


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(
        min_length=3,
        max_length=200
    )

    description: str | None = None

    priority: Literal["low", "medium", "high"] = "medium"

    assigned_to_id: int

    due_date: date | None = None


class TaskResponse(BaseModel):
    """Public task information returned by the API."""

    id: int
    title: str
    description: str | None
    status: str
    priority: str
    created_by_id: int
    assigned_to_id: int
    due_date: date | None

    model_config = ConfigDict(from_attributes=True)


class TaskReassign(BaseModel):
    """Schema for reassigning a task."""

    assigned_to_id: int = Field(gt=0)



class TaskHistoryResponse(BaseModel):
    """Task history information."""

    id: int
    task_id: int
    changed_by_id: int
    action: str
    old_status: str | None
    new_status: str | None
    old_assignee_id: int | None
    new_assignee_id: int | None
    remarks: str | None
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)



class TaskStatusUpdate(BaseModel):
    """Schema for updating task status."""

    status: Literal[
        "pending",
        "in_progress",
        "completed"
    ]


class TimeLogCreate(BaseModel):
    """Schema for logging working hours."""

    hours_worked: float = Field(
        gt=0,
        le=24
    )

    work_date: date

    description: str | None = None