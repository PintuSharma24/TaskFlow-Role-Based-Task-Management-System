from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.security import hash_password
from app.database.connection import get_db
from app.models.user import User
from app.schemas.admin import (
    EmployeeResponse,
    AdminManagerDetailsResponse,
    ManagerUpdate
)
from app.schemas.manager import ManagerResponse
from sqlalchemy import func

from app.models.task import Task
from app.schemas.admin import AdminDashboardResponse




router = APIRouter(
    prefix="/admin",
    tags=["Admin Management"]
)


@router.get(
    "/employees",
    response_model=list[EmployeeResponse]
)
def get_all_employees(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin"))
):
    employees = db.scalars(
        select(User)
        .where(User.role == "employee")
        .order_by(User.id)
    ).all()

    return employees

@router.get(
    "/managers/{manager_id}",
    response_model=AdminManagerDetailsResponse
)
def get_manager_details(
    manager_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin"))
):
    # Find the Manager
    manager = db.scalar(
        select(User).where(
            User.id == manager_id,
            User.role == "manager"
        )
    )

    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    # Find employees under this Manager
    employees = db.scalars(
        select(User)
        .where(
            User.role == "employee",
            User.manager_id == manager.id
        )
        .order_by(User.id)
    ).all()

    # Return Manager and team details
    return {
        "id": manager.id,
        "name": manager.name,
        "email": manager.email,
        "role": manager.role,
        "is_active": manager.is_active,
        "total_employees": len(employees),
        "employees": employees
    }


@router.patch(
    "/managers/{manager_id}",
    response_model=ManagerResponse
)
def update_manager(
    manager_id: int,
    manager_data: ManagerUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin"))
):
    # Find the Manager
    manager = db.scalar(
        select(User).where(
            User.id == manager_id,
            User.role == "manager"
        )
    )

    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    # Get only fields provided by Admin
    update_data = manager_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided"
        )

    # Reject null values
    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Update fields cannot be null"
        )

    # Check for duplicate email
    if "email" in update_data:
        new_email = str(update_data["email"]).lower()

        existing_user = db.scalar(
            select(User).where(
                User.email == new_email,
                User.id != manager.id
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered"
            )

        update_data["email"] = new_email

    # Hash password before saving
    if "password" in update_data:
        update_data["password_hash"] = hash_password(
            update_data.pop("password")
        )

    # Update Manager fields
    for field, value in update_data.items():
        setattr(manager, field, value)

    try:
        db.commit()
        db.refresh(manager)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update Manager"
        )

    return manager


@router.patch(
    "/managers/{manager_id}/deactivate",
    response_model=ManagerResponse
)
def deactivate_manager(
    manager_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin"))
):
    # Find the Manager
    manager = db.scalar(
        select(User).where(
            User.id == manager_id,
            User.role == "manager"
        )
    )

    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    # Check whether Manager is already inactive
    if not manager.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manager is already inactive"
        )

    # Deactivate Manager
    manager.is_active = False

    try:
        db.commit()
        db.refresh(manager)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not deactivate Manager"
        )

    return manager


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin"))
):
    # Manager statistics
    total_managers = db.scalar(
        select(func.count(User.id)).where(
            User.role == "manager"
        )
    ) or 0

    active_managers = db.scalar(
        select(func.count(User.id)).where(
            User.role == "manager",
            User.is_active == True
        )
    ) or 0

    inactive_managers = db.scalar(
        select(func.count(User.id)).where(
            User.role == "manager",
            User.is_active == False
        )
    ) or 0

    # Employee statistics
    total_employees = db.scalar(
        select(func.count(User.id)).where(
            User.role == "employee"
        )
    ) or 0

    active_employees = db.scalar(
        select(func.count(User.id)).where(
            User.role == "employee",
            User.is_active == True
        )
    ) or 0

    inactive_employees = db.scalar(
        select(func.count(User.id)).where(
            User.role == "employee",
            User.is_active == False
        )
    ) or 0

    # Task statistics
    total_tasks = db.scalar(
        select(func.count(Task.id))
    ) or 0

    pending_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.status == "pending"
        )
    ) or 0

    in_progress_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.status == "in_progress"
        )
    ) or 0

    completed_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.status == "completed"
        )
    ) or 0

    return {
        "total_managers": total_managers,
        "active_managers": active_managers,
        "inactive_managers": inactive_managers,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks
    }