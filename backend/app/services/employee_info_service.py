
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task
from app.models.time_log import TimeLog
from app.models.task_history import TaskHistory


def get_employee_report(
    db: Session,
    manager_id: int,
    employee_name: str
):
    """
    Retrieve complete available employee information
    for an authenticated Manager's team.
    """

    # 1. Find employee within the Manager's own team
    employees = db.execute(
        select(User).where(
            User.role == "employee",
            User.manager_id == manager_id,
            func.lower(User.name) == employee_name.strip().lower()
        )
    ).scalars().all()

    if not employees:
        return {
            "found": False,
            "message": "No employee with that name was found in your team."
        }

    if len(employees) > 1:
        return {
            "found": False,
            "message": (
                "Multiple employees have this name. "
                "Please provide their email address to identify the correct employee."
            )
        }

    employee = employees[0]

    # 2. Retrieve Manager information
    manager = db.get(User, manager_id)

    # 3. Retrieve all currently assigned tasks
    tasks = db.execute(
        select(Task)
        .where(Task.assigned_to_id == employee.id)
        .order_by(Task.created_at.desc())
    ).scalars().all()

    task_ids = [task.id for task in tasks]

    # 4. Calculate task statistics
    total_tasks = len(tasks)

    task_statistics = {
        "total": total_tasks,
        "pending": sum(1 for task in tasks if task.status == "pending"),
        "in_progress": sum(
            1 for task in tasks if task.status == "in_progress"
        ),
        "completed": sum(
            1 for task in tasks if task.status == "completed"
        )
    }

    # 5. Retrieve employee time logs with task titles
    time_log_results = db.execute(
        select(TimeLog, Task.title)
        .join(Task, TimeLog.task_id == Task.id)
        .where(TimeLog.employee_id == employee.id)
        .order_by(TimeLog.work_date.desc(), TimeLog.id.desc())
    ).all()

    time_logs = []

    for log, task_title in time_log_results:
        time_logs.append({
            "time_log_id": log.id,
            "task_id": log.task_id,
            "task_title": task_title,
            "hours_worked": float(log.hours_worked),
            "work_date": log.work_date.isoformat(),
            "description": log.description or "No description provided",
            "created_at": log.created_at.isoformat()
        })

    total_hours = sum(
        log["hours_worked"] for log in time_logs
    )

    # 6. Retrieve task history, including reassignment activity
    history_query = (
        select(TaskHistory, Task.title)
        .join(Task, TaskHistory.task_id == Task.id)
        .where(
            or_(
                TaskHistory.task_id.in_(task_ids),
                TaskHistory.old_assignee_id == employee.id,
                TaskHistory.new_assignee_id == employee.id
            )
        )
        .order_by(TaskHistory.changed_at.desc())
    )

    history_results = db.execute(history_query).all()

    task_history = []

    for history, task_title in history_results:
        task_history.append({
            "history_id": history.id,
            "task_id": history.task_id,
            "task_title": task_title,
            "action": history.action,
            "old_status": history.old_status,
            "new_status": history.new_status,
            "old_assignee_id": history.old_assignee_id,
            "new_assignee_id": history.new_assignee_id,
            "changed_by_id": history.changed_by_id,
            "remarks": history.remarks,
            "changed_at": history.changed_at.isoformat()
        })

    # 7. Prepare complete employee report
    return {
        "found": True,

        "employee": {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "role": employee.role,
            "is_active": employee.is_active,
            "manager_name": manager.name if manager else None,
            "created_at": employee.created_at.isoformat()
        },

        "task_statistics": task_statistics,

        "assigned_tasks": [
            {
                "task_id": task.id,
                "title": task.title,
                "description": task.description or "No description provided",
                "status": task.status,
                "priority": task.priority,
                "due_date": (
                    task.due_date.isoformat()
                    if task.due_date else None
                ),
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ],

        "time_summary": {
            "total_time_logs": len(time_logs),
            "total_hours_worked": round(total_hours, 2),
            "time_logs": time_logs
        },

        "task_history": task_history
    }




def get_employee_targeted_report(
    db: Session,
    manager_id: int,
    employee_name: str,
    intent: str = "overview"
):
    """
    Return only the employee information needed for the question.
    Uses the existing employee report and filters its results.
    """

    report = get_employee_report(
        db=db,
        manager_id=manager_id,
        employee_name=employee_name
    )

    if not report.get("found"):
        return report

    employee = report["employee"]
    tasks = report["assigned_tasks"]
    task_statistics = report["task_statistics"]
    time_summary = report["time_summary"]
    task_history = report["task_history"]

    # 1. Employee overview
    if intent == "overview":
        return {
            "found": True,
            "intent": intent,
            "employee": employee,
            "task_statistics": task_statistics,
            "time_summary": {
                "total_time_logs": time_summary["total_time_logs"],
                "total_hours_worked": time_summary["total_hours_worked"]
            }
        }

    # 2. All assigned tasks
    if intent == "tasks":
        return {
            "found": True,
            "intent": intent,
            "employee": employee,
            "assigned_tasks": tasks
        }

    # 3. Tasks filtered by status
    if intent in {"pending", "in_progress", "completed"}:
        filtered_tasks = [
            task for task in tasks
            if task["status"] == intent
        ]

        return {
            "found": True,
            "intent": intent,
            "employee": employee,
            "task_count": len(filtered_tasks),
            "assigned_tasks": filtered_tasks
        }

    # 4. Detailed time logs
    if intent == "time_logs":
        return {
            "found": True,
            "intent": intent,
            "employee": employee,
            "time_summary": time_summary
        }

    # 5. Total hours only
    if intent == "hours":
        return {
            "found": True,
            "intent": intent,
            "employee": employee,
            "total_time_logs": time_summary["total_time_logs"],
            "total_hours_worked": time_summary["total_hours_worked"]
        }

    # 6. Task history
    if intent == "history":
        return {
            "found": True,
            "intent": intent,
            "employee": employee,
            "task_history": task_history
        }

    # Default to employee overview
    return {
        "found": True,
        "intent": "overview",
        "employee": employee,
        "task_statistics": task_statistics,
        "time_summary": {
            "total_time_logs": time_summary["total_time_logs"],
            "total_hours_worked": time_summary["total_hours_worked"]
        }
    }
