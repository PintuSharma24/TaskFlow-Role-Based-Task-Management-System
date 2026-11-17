from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database.connection import get_db
from app.models.user import User
from app.schemas.manager import EmployeeResponse
from sqlalchemy import select
from app.models.task import Task
from app.schemas.task import TaskResponse
from fastapi import HTTPException, status
from app.models.task_history import TaskHistory
from app.schemas.task import TaskStatusUpdate
from app.models.time_log import TimeLog
from app.schemas.task import TimeLogCreate
from app.models.time_log import TimeLog



router = APIRouter(
    prefix="/employee",
    tags=["Employee Management"]
)


@router.get(
    "/profile",
    response_model=EmployeeResponse
)
def get_my_profile(
    current_employee: User = Depends(
        require_roles("employee")
    )
):
    return current_employee

@router.get(
    "/tasks",
    response_model=list[TaskResponse]
)
def get_my_assigned_tasks(
    db: Session = Depends(get_db),
    current_employee: User = Depends(
        require_roles("employee")
    )
):
    tasks = db.scalars(
        select(Task)
        .where(
            Task.assigned_to_id == current_employee.id
        )
        .order_by(Task.id.desc())
    ).all()

    return tasks


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def get_task_details(
    task_id: int,
    db: Session = Depends(get_db),
    current_employee: User = Depends(
        require_roles("employee")
    )
):
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.assigned_to_id == current_employee.id
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in your assigned tasks"
        )

    return task


@router.patch(
    "/tasks/{task_id}/status",
    response_model=TaskResponse
)
def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_employee: User = Depends(
        require_roles("employee")
    )
):
    # Find task assigned to the logged-in Employee
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.assigned_to_id == current_employee.id
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in your assigned tasks"
        )

    # Get the requested status
    new_status = status_data.status
    old_status = task.status

    if old_status == new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already has this status"
        )

    # Validate status transitions
    allowed_transitions = {
        "pending": ["in_progress"],
        "in_progress": ["pending", "completed"],
        "completed": []
    }

    if new_status not in allowed_transitions[old_status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task status transition"
        )

    # Update task status
    task.status = new_status

    # Record status change
    history = TaskHistory(
        task_id=task.id,
        changed_by_id=current_employee.id,
        action="status_updated",
        old_status=old_status,
        new_status=new_status,
        remarks="Task status updated by Employee"
    )

    try:
        db.add(history)
        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update task status"
        )

    return task

@router.post(
    "/tasks/{task_id}/time-logs",
    status_code=status.HTTP_201_CREATED
)
def log_working_hours(
    task_id: int,
    time_log_data: TimeLogCreate,
    db: Session = Depends(get_db),
    current_employee: User = Depends(
        require_roles("employee")
    )
):
    # Verify that the task belongs to this Employee
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.assigned_to_id == current_employee.id
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in your assigned tasks"
        )

    # Create time log
    time_log = TimeLog(
        task_id=task.id,
        employee_id=current_employee.id,
        hours_worked=time_log_data.hours_worked,
        work_date=time_log_data.work_date,
        description=time_log_data.description
    )

    try:
        db.add(time_log)
        db.commit()
        db.refresh(time_log)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not log working hours"
        )

    return {
        "message": "Working hours logged successfully",
        "time_log_id": time_log.id,
        "task_id": time_log.task_id,
        "employee_id": time_log.employee_id,
        "hours_worked": float(time_log.hours_worked),
        "work_date": time_log.work_date,
        "description": time_log.description
    }

@router.get("/time-logs")
def get_my_time_logs(
    db: Session = Depends(get_db),
    current_employee: User = Depends(require_roles("employee"))
):
    time_logs = db.scalars(
        select(TimeLog)
        .where(TimeLog.employee_id == current_employee.id)
        .order_by(TimeLog.work_date.desc())
    ).all()

    return [
        {
            "id": log.id,
            "task_id": log.task_id,
            "employee_id": log.employee_id,
            "hours_worked": float(log.hours_worked),
            "work_date": log.work_date,
            "description": log.description
        }
        for log in time_logs
    ]