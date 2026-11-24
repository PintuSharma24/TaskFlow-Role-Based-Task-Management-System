
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.security import hash_password
from app.database.connection import get_db
from app.models.user import User
from app.schemas.manager import ManagerCreate, ManagerResponse
from app.schemas.manager import EmployeeCreate, EmployeeResponse
from app.schemas.manager import EmployeeUpdate
from app.schemas.manager import EmployeePaginationResponse

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse
from app.models.task_history import TaskHistory
from app.schemas.task import TaskReassign
from app.schemas.task import TaskHistoryResponse
from app.models.time_log import TimeLog

router = APIRouter(
    prefix="/managers",
    tags=["Manager Management"]
)


@router.post(
    "/",
    response_model=ManagerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_manager(
    manager_data: ManagerCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin"))
):
    # Check whether email is already registered
    existing_user = db.scalar(
        select(User).where(User.email == manager_data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    # Create Manager with hashed password
    manager = User(
        name=manager_data.name,
        email=str(manager_data.email).lower(),
        password_hash=hash_password(manager_data.password),
        role="manager",
        is_active=True,
        manager_id=None
    )

    try:
        db.add(manager)
        db.commit()
        db.refresh(manager)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create Manager"
        )

    return manager


@router.get(
    "/",
    response_model=list[ManagerResponse]
)
def get_all_managers(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("admin"))
):
    managers = db.scalars(
        select(User).where(User.role == "manager").order_by(User.id)
    ).all()

    return managers

@router.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    # Check whether email is already registered
    existing_user = db.scalar(
        select(User).where(
            User.email == str(employee_data.email).lower()
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    # Create Employee under the logged-in Manager
    employee = User(
        name=employee_data.name,
        email=str(employee_data.email).lower(),
        password_hash=hash_password(employee_data.password),
        role="employee",
        is_active=True,
        manager_id=current_manager.id
    )

    try:
        db.add(employee)
        db.commit()
        db.refresh(employee)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create Employee"
        )

    return employee



@router.get(
    "/employees",
    response_model=EmployeePaginationResponse
)
def get_my_employees(
    page: int = 1,
    limit: int = 10,
    sort_by: str = "name",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than or equal to 1"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100"
        )

    # Allowed sorting fields
    allowed_sort_fields = {
        "name": User.name,
        "email": User.email,
        "created_at": User.created_at
    }

    # Validate sorting field
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort field. Use name, email, or created_at."
        )

    # Validate sorting order
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort order. Use asc or desc."
        )

    # Base query: only employees belonging to this Manager
    employee_query = select(User).where(
        User.role == "employee",
        User.manager_id == current_manager.id
    )

    # Count total employees
    total = db.scalar(
        select(func.count())
        .select_from(User)
        .where(
            User.role == "employee",
            User.manager_id == current_manager.id
        )
    ) or 0

    # Calculate total pages
    total_pages = (total + limit - 1) // limit

    
    # Apply sorting
    sort_column = allowed_sort_fields[sort_by]

    if order == "asc":
        employee_query = employee_query.order_by(
            sort_column.asc(),
            User.id.asc()
        )
    else:
        employee_query = employee_query.order_by(
            sort_column.desc(),
            User.id.asc()
        )

    # Apply server-side pagination
    employees = db.scalars(
        employee_query
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()


    return {
        "items": employees,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }




@router.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee_details(
    employee_id: int,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    employee = db.scalar(
        select(User).where(
            User.id == employee_id,
            User.role == "employee",
            User.manager_id == current_manager.id
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found in your team"
        )

    return employee


@router.patch(
    "/employees/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    # Find employee belonging to the logged-in Manager
    employee = db.scalar(
        select(User).where(
            User.id == employee_id,
            User.role == "employee",
            User.manager_id == current_manager.id
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found in your team"
        )

    # Get only the fields provided by Manager
    update_data = employee_data.model_dump(exclude_unset=True)

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

    # Check duplicate email
    if "email" in update_data:
        new_email = str(update_data["email"]).lower()

        existing_user = db.scalar(
            select(User).where(
                User.email == new_email,
                User.id != employee.id
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered"
            )

        update_data["email"] = new_email

    # Securely hash a new password
    if "password" in update_data:
        update_data["password_hash"] = hash_password(
            update_data.pop("password")
        )

    # Apply updates
    for field, value in update_data.items():
        setattr(employee, field, value)

    try:
        db.commit()
        db.refresh(employee)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update Employee"
        )

    return employee


@router.patch(
    "/employees/{employee_id}/deactivate",
    response_model=EmployeeResponse
)
def deactivate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    # Find employee belonging to the logged-in Manager
    employee = db.scalar(
        select(User).where(
            User.id == employee_id,
            User.role == "employee",
            User.manager_id == current_manager.id
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found in your team"
        )

    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee is already inactive"
        )

    # Deactivate employee
    employee.is_active = False

    try:
        db.commit()
        db.refresh(employee)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not deactivate Employee"
        )

    return employee


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    # Check whether the employee belongs to this Manager
    employee = db.scalar(
        select(User).where(
            User.id == task_data.assigned_to_id,
            User.role == "employee",
            User.manager_id == current_manager.id,
            User.is_active == True
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active employee not found in your team"
        )

    # Create the task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        assigned_to_id=employee.id,
        created_by_id=current_manager.id,
        due_date=task_data.due_date
    )

    try:
        db.add(task)
        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create task"
        )

    return task


@router.patch(
    "/tasks/{task_id}/reassign",
    response_model=TaskResponse
)
def reassign_task(
    task_id: int,
    reassign_data: TaskReassign,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    # Find the task created by this Manager
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.created_by_id == current_manager.id
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in your records"
        )

    # Find the new employee in this Manager's active team
    new_employee = db.scalar(
        select(User).where(
            User.id == reassign_data.assigned_to_id,
            User.role == "employee",
            User.manager_id == current_manager.id,
            User.is_active == True
        )
    )

    if new_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active employee not found in your team"
        )

    # Prevent reassignment to the same employee
    if task.assigned_to_id == new_employee.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is already assigned to this employee"
        )

    # Store previous assignee
    old_assignee_id = task.assigned_to_id

    # Update task assignment
    task.assigned_to_id = new_employee.id

    # Record reassignment in task history
    history = TaskHistory(
        task_id=task.id,
        changed_by_id=current_manager.id,
        action="reassigned",
        old_assignee_id=old_assignee_id,
        new_assignee_id=new_employee.id,
        remarks="Task reassigned by Manager"
    )

    try:
        db.add(history)
        db.commit()
        db.refresh(task)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not reassign task"
        )

    return task

@router.get(
    "/tasks",
    response_model=list[TaskResponse]
)
def get_my_tasks(
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    tasks = db.scalars(
        select(Task)
        .where(
            Task.created_by_id == current_manager.id
        )
        .order_by(Task.id.desc())
    ).all()

    return tasks



@router.get(
    "/tasks/{task_id}/history",
    response_model=list[TaskHistoryResponse]
)
def get_task_history(
    task_id: int,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    # Verify that the task belongs to this Manager
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.created_by_id == current_manager.id
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in your records"
        )

    # Fetch history of this task
    history_records = db.scalars(
        select(TaskHistory)
        .where(TaskHistory.task_id == task.id)
        .order_by(TaskHistory.changed_at.desc())
    ).all()

    return history_records


@router.get("/time-logs")
def get_team_time_logs(
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_roles("manager"))
):
    results = db.execute(
        select(TimeLog, User, Task)
        .join(User, TimeLog.employee_id == User.id)
        .join(Task, TimeLog.task_id == Task.id)
        .where(User.manager_id == current_manager.id)
        .order_by(TimeLog.work_date.desc())
    ).all()

    return [
        {
            "id": log.id,
            "task_id": task.id,
            "task_title": task.title,
            "employee_id": employee.id,
            "employee_name": employee.name,
            "hours_worked": float(log.hours_worked),
            "work_date": log.work_date,
            "description": log.description
        }
        for log, employee, task in results
    ]
