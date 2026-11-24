
import os
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select

from app.database.connection import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.task import Task
from app.models.task_history import TaskHistory
from app.models.time_log import TimeLog


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

TARGET_EMPLOYEES = 100
TARGET_TASKS = 500

DEFAULT_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")

if not DEFAULT_PASSWORD:
    raise ValueError(
        "Please set SEED_DEFAULT_PASSWORD in PowerShell before running."
    )

random.seed(42)

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Reyansh",
    "Krishna", "Ishaan", "Kabir", "Rohan", "Rahul",
    "Neha", "Priya", "Ananya", "Kavya", "Isha",
    "Sneha", "Pooja", "Aditi", "Meera", "Riya",
    "Sahil", "Karan", "Nikhil", "Varun", "Aman",
    "Simran", "Tanya", "Shreya", "Divya", "Anjali"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Yadav",
    "Mehta", "Jain", "Agarwal", "Kumar", "Malhotra",
    "Patel", "Joshi", "Rathore", "Saxena", "Mishra"
]

TASK_TEMPLATES = [
    (
        "Prepare Monthly Sales Report",
        "Analyze monthly sales data, identify trends, and prepare a detailed report."
    ),
    (
        "Customer Data Validation",
        "Review customer records and correct missing or inconsistent information."
    ),
    (
        "API Testing and Documentation",
        "Test API endpoints, validate responses, and document the results."
    ),
    (
        "Employee Attendance Report",
        "Review attendance records and prepare the monthly attendance summary."
    ),
    (
        "Project Documentation Update",
        "Review project documentation and update outdated information."
    ),
    (
        "Database Quality Check",
        "Validate database records and identify duplicate or incomplete entries."
    ),
    (
        "Weekly Performance Analysis",
        "Analyze weekly performance metrics and prepare management insights."
    ),
    (
        "Customer Feedback Analysis",
        "Review customer feedback and identify recurring issues."
    ),
    (
        "Task Progress Review",
        "Review assigned tasks and prepare a progress summary."
    ),
    (
        "Inventory Data Verification",
        "Verify inventory records and report discrepancies."
    ),
]


def get_count(db, model):
    return db.scalar(select(func.count()).select_from(model)) or 0


def main():
    db = SessionLocal()

    try:
        print("\nStarting TaskFlow data enhancement...\n")

        # --------------------------------------------------
        # 1. FETCH MANAGERS
        # --------------------------------------------------

        managers = db.scalars(
            select(User)
            .where(
                User.role == "manager",
                User.is_active.is_(True)
            )
            .order_by(User.id)
        ).all()

        if not managers:
            raise ValueError("No active managers found in database.")

        print(f"Active managers found: {len(managers)}")

        # --------------------------------------------------
        # 2. CREATE EMPLOYEES
        # --------------------------------------------------

        employee_counts = {}

        for manager in managers:
            count = db.scalar(
                select(func.count())
                .select_from(User)
                .where(
                    User.role == "employee",
                    User.manager_id == manager.id
                )
            ) or 0

            employee_counts[manager.id] = count

        total_employees = sum(employee_counts.values())
        password_hash = hash_password(DEFAULT_PASSWORD)

        employee_number = 1

        for manager in managers:
            current_count = employee_counts[manager.id]
            required_count = max(0, 25 - current_count)

            print(
                f"{manager.name}: "
                f"{current_count} existing, "
                f"adding {required_count}"
            )

            for _ in range(required_count):
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)

                employee = User(
                    name=f"{first_name} {last_name}",
                    email=(
                        f"taskflow.employee{employee_number:03d}"
                        "@example.com"
                    ),
                    password_hash=password_hash,
                    role="employee",
                    is_active=True,
                    manager_id=manager.id
                )

                db.add(employee)
                employee_number += 1

        db.flush()

        # --------------------------------------------------
        # 3. FETCH EMPLOYEES BY MANAGER
        # --------------------------------------------------

        team_members = {}

        for manager in managers:
            employees = db.scalars(
                select(User).where(
                    User.role == "employee",
                    User.manager_id == manager.id,
                    User.is_active.is_(True)
                )
            ).all()

            if not employees:
                raise ValueError(
                    f"No active employees found for {manager.name}"
                )

            team_members[manager.id] = employees

        # --------------------------------------------------
        # 4. CREATE TASKS
        # --------------------------------------------------

        current_tasks = get_count(db, Task)
        tasks_to_create = max(0, TARGET_TASKS - current_tasks)

        print(f"\nExisting tasks: {current_tasks}")
        print(f"New tasks to create: {tasks_to_create}")

        statuses = ["pending", "in_progress", "completed"]
        priorities = ["low", "medium", "high"]

        for index in range(tasks_to_create):
            manager = managers[index % len(managers)]
            employees = team_members[manager.id]

            # Select a final assigned employee and another
            # employee to represent a previous assignment.
            assigned_employee, previous_employee = random.sample(
                employees, 2
            )

            title, description = random.choice(TASK_TEMPLATES)

            task = Task(
                title=f"{title} #{index + 1}",
                description=description,
                status=random.choice(statuses),
                priority=random.choice(priorities),
                created_by_id=manager.id,
                assigned_to_id=assigned_employee.id,
                due_date=date.today() + timedelta(
                    days=random.randint(-10, 60)
                )
            )

            db.add(task)
            db.flush()

            # --------------------------------------------------
            # 5. CREATE REASSIGNMENT HISTORY
            # --------------------------------------------------

            db.add(
                TaskHistory(
                    task_id=task.id,
                    changed_by_id=manager.id,
                    action="reassigned",
                    old_assignee_id=previous_employee.id,
                    new_assignee_id=assigned_employee.id,
                    remarks="Task reassigned by Manager"
                )
            )

            # --------------------------------------------------
            # 6. CREATE STATUS HISTORY
            # --------------------------------------------------

            # The history follows valid status transitions.
            # The final task status matches the Task record.

            status_history = []

            if task.status == "pending":
                status_history = [
                    ("pending", "in_progress"),
                    ("in_progress", "pending")
                ]

            elif task.status == "in_progress":
                status_history = [
                    ("pending", "in_progress"),
                    ("in_progress", "pending"),
                    ("pending", "in_progress")
                ]

            elif task.status == "completed":
                status_history = [
                    ("pending", "in_progress"),
                    ("in_progress", "completed")
                ]

            for old_status, new_status in status_history:
                db.add(
                    TaskHistory(
                        task_id=task.id,
                        changed_by_id=assigned_employee.id,
                        action="status_updated",
                        old_status=old_status,
                        new_status=new_status,
                        remarks="Task status updated by Employee"
                    )
                )

            # --------------------------------------------------
            # 7. CREATE TIME LOGS
            # --------------------------------------------------

            for log_number in range(3):
                work_date = date.today() - timedelta(
                    days=random.randint(0, 90)
                )

                hours = Decimal(
                    str(round(random.uniform(1.0, 8.0), 2))
                )

                db.add(
                    TimeLog(
                        task_id=task.id,
                        employee_id=assigned_employee.id,
                        hours_worked=hours,
                        work_date=work_date,
                        description=(
                            f"Work session {log_number + 1}: "
                            f"Task progress and execution."
                        )
                    )
                )

            if (index + 1) % 50 == 0:
                print(f"Generated {index + 1} tasks...")

        # --------------------------------------------------
        # 8. COMMIT ALL CHANGES
        # --------------------------------------------------

        db.commit()

        print("\nData enhancement completed successfully!")

        print("\nFINAL DATABASE COUNTS")
        print("-----------------------------")
        print(f"Users:        {get_count(db, User)}")
        print(f"Tasks:        {get_count(db, Task)}")
        print(f"Task History: {get_count(db, TaskHistory)}")
        print(f"Time Logs:    {get_count(db, TimeLog)}")

        print("\nEMPLOYEE DISTRIBUTION")

        for manager in managers:
            count = db.scalar(
                select(func.count())
                .select_from(User)
                .where(
                    User.role == "employee",
                    User.manager_id == manager.id
                )
            ) or 0

            print(f"{manager.name}: {count} employees")

    except Exception as error:
        db.rollback()
        print("\nError occurred. All changes were rolled back.")
        print(f"Error: {error}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
