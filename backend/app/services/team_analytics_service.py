
from datetime import date

from sqlalchemy import select, func, case
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task
from app.models.time_log import TimeLog


def get_team_overview(db: Session, manager_id: int):
    """Return employee, task and work-hour statistics for one Manager."""

    employee_count = db.scalar(
        select(func.count(User.id)).where(
            User.role == "employee",
            User.manager_id == manager_id
        )
    ) or 0

    task_counts = db.execute(
        select(
            Task.status,
            func.count(Task.id)
        )
        .join(User, Task.assigned_to_id == User.id)
        .where(User.manager_id == manager_id)
        .group_by(Task.status)
    ).all()

    task_statistics = {
        "total": 0,
        "pending": 0,
        "in_progress": 0,
        "completed": 0
    }

    for status, count in task_counts:
        task_statistics["total"] += count
        if status in task_statistics:
            task_statistics[status] = count

    total_hours = db.scalar(
        select(func.coalesce(func.sum(TimeLog.hours_worked), 0))
        .join(User, TimeLog.employee_id == User.id)
        .where(User.manager_id == manager_id)
    ) or 0

    return {
        "employee_count": employee_count,
        "task_statistics": task_statistics,
        "total_hours_worked": round(float(total_hours), 2)
    }


def get_employee_pending_workload(db: Session, manager_id: int):
    """List employees and their pending task counts."""

    results = db.execute(
        select(
            User.id,
            User.name,
            User.email,
            func.count(Task.id).label("pending_count")
        )
        .outerjoin(
            Task,
            (Task.assigned_to_id == User.id)
            & (Task.status == "pending")
        )
        .where(
            User.role == "employee",
            User.manager_id == manager_id
        )
        .group_by(User.id, User.name, User.email)
        .order_by(func.count(Task.id).desc(), User.name.asc())
    ).all()

    return [
        {
            "employee_id": row.id,
            "name": row.name,
            "email": row.email,
            "pending_tasks": row.pending_count
        }
        for row in results
    ]


def get_team_overdue_tasks(db: Session, manager_id: int):
    """Find overdue tasks assigned to employees in this Manager's team."""

    today = date.today()

    results = db.execute(
        select(Task, User.name, User.email)
        .join(User, Task.assigned_to_id == User.id)
        .where(
            User.role == "employee",
            User.manager_id == manager_id,
            Task.due_date < today,
            Task.status != "completed"
        )
        .order_by(Task.due_date.asc())
    ).all()

    return [
        {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat(),
            "employee_name": employee_name,
            "employee_email": employee_email
        }
        for task, employee_name, employee_email in results
    ]



def get_employee_overdue_tasks(
    db: Session,
    manager_id: int,
    employee_id: int
):
    today = date.today()

    results = db.execute(
        select(Task)
        .join(User, Task.assigned_to_id == User.id)
        .where(
            User.id == employee_id,
            User.role == "employee",
            User.manager_id == manager_id,
            Task.due_date < today,
            Task.status != "completed"
        )
        .order_by(Task.due_date.asc())
    ).scalars().all()

    return [
        {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat()
        }
        for task in results
    ]