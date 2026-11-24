
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.employee_info_service import (
    get_employee_targeted_report,
)
from app.services.rag_service import ask_manager_question

from app.services.team_analytics_service import (
    get_team_overview,
    get_employee_pending_workload,
    get_team_overdue_tasks,
    get_employee_overdue_tasks,
)

from app.services.ollama_service import generate_response



def is_greeting(question: str) -> bool:
    greetings = {
        "hi", "hello", "hey", "good morning",
        "good afternoon", "good evening",
        "how are you", "what's up", "whats up"
    }
    return question.strip().lower() in greetings


def find_employee_in_question(
    db: Session,
    manager_id: int,
    question: str
):
    """Find employees only within the authenticated Manager's team."""

    employees = db.execute(
        select(User).where(
            User.role == "employee",
            User.manager_id == manager_id
        )
    ).scalars().all()

    matches = []

    for employee in employees:
        name_parts = employee.name.lower().split()

        # Match full name or any distinctive name part.
        for part in name_parts:
            if len(part) <= 2:
                continue

            pattern = rf"\b{re.escape(part)}\b"

            if re.search(pattern, question.lower()):
                matches.append(employee)
                break

    return matches


def detect_employee_intent(question: str) -> str:
    """Identify which employee information the Manager is requesting."""

    q = question.lower()

    if any(word in q for word in [
        "history", "historical", "status change",
        "reassigned", "reassignment", "task changes"
    ]):
        return "history"

    if any(word in q for word in [
        "time log", "time logs", "timesheet",
        "work log", "work logs", "logged time"
    ]):
        return "time_logs"

    if any(word in q for word in [
        "how many hours", "total hours", "hours worked",
        "worked hours", "total time"
    ]):
        return "hours"

    if any(word in q for word in [
        "pending", "not started", "incomplete"
    ]):
        return "pending"

    if any(word in q for word in [
        "in progress", "in-progress", "ongoing"
    ]):
        return "in_progress"

    if any(word in q for word in [
        "completed", "complete", "finished", "done"
    ]):
        return "completed"

    if any(word in q for word in [
        "task", "tasks", "assignment", "assignments",
        "assigned work", "what work"
    ]):
        return "tasks"

    return "overview"


def detect_team_intent(question: str):
    """Detect Manager questions about the entire team."""

    q = question.lower()

    # Pending workload ranking
    if any(phrase in q for phrase in [
        "most pending",
        "highest pending",
        "pending workload",
        "workload",
        "most tasks",
        "highest number of tasks"
    ]):
        return "workload"

    # Overdue tasks
    if any(phrase in q for phrase in [
        "overdue",
        "over due",
        "past due",
        "late tasks",
        "missed deadline"
    ]):
        return "overdue"

    # Team overview and statistics
    if any(phrase in q for phrase in [
        "my team",
        "team overview",
        "team statistics",
        "team stats",
        "across the team",
        "team members",
        "how many employees",
        "total employees",
        "total team hours",
        "team pending tasks",
        "team completed tasks"
    ]):
        return "overview"

    return None


def format_team_analytics(db: Session, manager_id: int, intent: str):
    """Get and format team analytics from SQL database."""

    if intent == "overview":
        data = get_team_overview(db, manager_id)
        stats = data["task_statistics"]

        return (
            "TEAM OVERVIEW\n\n"
            f"Total employees: {data['employee_count']}\n"
            f"Total tasks: {stats['total']}\n"
            f"Pending tasks: {stats['pending']}\n"
            f"In-progress tasks: {stats['in_progress']}\n"
            f"Completed tasks: {stats['completed']}\n"
            f"Total team hours worked: {data['total_hours_worked']}"
        )

    if intent == "workload":
        employees = get_employee_pending_workload(db, manager_id)

        if not employees:
            return "No employees were found in your team."

        lines = ["TEAM PENDING WORKLOAD\n"]

        for employee in employees:
            lines.append(
                f"{employee['name']} ({employee['email']}) - "
                f"{employee['pending_tasks']} pending tasks"
            )

        return "\n".join(lines)

    if intent == "overdue":
        tasks = get_team_overdue_tasks(db, manager_id)

        if not tasks:
            return "Your team has no overdue incomplete tasks."

        lines = [f"OVERDUE TASKS: {len(tasks)}\n"]

        for task in tasks:
            lines.extend([
                f"Task ID: {task['task_id']}",
                f"Title: {task['title']}",
                f"Description: {task['description']}",
                f"Employee: {task['employee_name']}",
                f"Email: {task['employee_email']}",
                f"Status: {task['status']}",
                f"Priority: {task['priority']}",
                f"Due date: {task['due_date']}",
                ""
            ])

        return "\n".join(lines)

    return "I couldn't identify the team analytics you requested."


def format_targeted_employee_report(report: dict) -> str:
    """Format targeted SQL results directly, without LLM-generated facts."""

    employee = report["employee"]
    intent = report.get("intent", "overview")

    lines = [
        f"Employee: {employee['name']}",
        f"Email: {employee['email']}",
        f"Role: {employee['role']}",
        f"Active: {'Yes' if employee['is_active'] else 'No'}",
        f"Manager: {employee['manager_name'] or 'Not available'}",
        ""
    ]

    if intent == "overview":
        stats = report["task_statistics"]
        time_summary = report["time_summary"]

        lines.extend([
            "EMPLOYEE OVERVIEW",
            f"Total tasks: {stats['total']}",
            f"Pending tasks: {stats['pending']}",
            f"In-progress tasks: {stats['in_progress']}",
            f"Completed tasks: {stats['completed']}",
            f"Total time logs: {time_summary['total_time_logs']}",
            f"Total hours worked: {time_summary['total_hours_worked']}"
        ])

    elif intent in {"tasks", "pending", "in_progress", "completed"}:
        tasks = report.get("assigned_tasks", [])

        lines.extend([
            "ASSIGNED TASKS",
            f"Number of tasks: {report.get('task_count', len(tasks))}"
        ])

        if not tasks:
            lines.append("No matching tasks were found.")

        for task in tasks:
            lines.extend([
                "",
                f"Task ID: {task['task_id']}",
                f"Title: {task['title']}",
                f"Description: {task['description']}",
                f"Status: {task['status']}",
                f"Priority: {task['priority']}",
                f"Due date: {task['due_date'] or 'Not specified'}",
                f"Created at: {task['created_at']}",
                f"Updated at: {task['updated_at']}"
            ])

    elif intent == "hours":
        lines.extend([
            "WORK HOURS SUMMARY",
            f"Total time logs: {report['total_time_logs']}",
            f"Total hours worked: {report['total_hours_worked']}"
        ])

    elif intent == "time_logs":
        summary = report["time_summary"]
        logs = summary["time_logs"]

        lines.extend([
            "TIME LOG SUMMARY",
            f"Total time logs: {summary['total_time_logs']}",
            f"Total hours worked: {summary['total_hours_worked']}",
            "",
            "TIME LOG DETAILS"
        ])

        if not logs:
            lines.append("No time logs were found.")

        for log in logs:
            lines.extend([
                "",
                f"Time log ID: {log['time_log_id']}",
                f"Task: {log['task_title']} (ID {log['task_id']})",
                f"Work date: {log['work_date']}",
                f"Hours worked: {log['hours_worked']}",
                f"Description: {log['description']}",
                f"Log created at: {log['created_at']}"
            ])

        lines.extend([
            "",
            "Note: The database stores work date, hours worked, and "
            "log creation time. It does not store clock-in or clock-out times."
        ])

    elif intent == "history":
        history_records = report.get("task_history", [])

        lines.extend([
            "TASK HISTORY",
            f"History records: {len(history_records)}"
        ])

        if not history_records:
            lines.append("No task history records were found.")

        for record in history_records:
            lines.extend([
                "",
                f"History ID: {record['history_id']}",
                f"Task: {record['task_title']} (ID {record['task_id']})",
                f"Action: {record['action']}",
                f"Old status: {record['old_status']}",
                f"New status: {record['new_status']}",
                f"Previous assignee ID: {record['old_assignee_id']}",
                f"New assignee ID: {record['new_assignee_id']}",
                f"Changed by user ID: {record['changed_by_id']}",
                f"Remarks: {record['remarks']}",
                f"Changed at: {record['changed_at']}"
            ])

    return "\n".join(lines)

def should_use_rag(question: str) -> bool:
    """
    Identify questions that need TaskFlow's stored knowledge
    rather than general LLM knowledge.
    """
    q = question.lower()

    rag_keywords = [
        "task history",
        "project documentation",
        "our project",
        "our task records",
        "based on our tasks",
        "based on task history",
        "from our records",
        "from task descriptions",
        "recurring issues",
        "patterns in our tasks",
        "what happened in our project",
        "summarize our project"
    ]

    return any(keyword in q for keyword in rag_keywords)




async def process_manager_question(
    db: Session,
    manager_id: int,
    question: str
):
    # 1. Handle greetings first.
    if is_greeting(question):
        return {
            "answer": (
                "Hello! Welcome to TaskFlow AI. I can help you with "
                "employee details, assigned tasks, pending work, "
                "time logs, work hours and task history. What would "
                "you like to know?"
            ),
            "sources": []
        }

    # 2. Identify whether the question is about a specific employee.
    # Employee-specific questions must be handled before team analytics.
    employees = find_employee_in_question(
        db=db,
        manager_id=manager_id,
        question=question
    )

    if len(employees) > 1:
        candidates = "\\n".join(
            f"- {employee.name} ({employee.email})"
            for employee in employees
        )

        return {
            "answer": (
                "I found multiple employees matching your question. "
                "Please specify which employee you mean:\\n"
                + candidates
            ),
            "sources": []
        }

    if len(employees) == 1:
        employee = employees[0]
        question_lower = question.lower()

        # Handle employee-specific overdue task questions directly from SQL.
        overdue_keywords = [
            "overdue",
            "over due",
            "past due",
            "late tasks",
            "missed deadline"
        ]

        if any(keyword in question_lower for keyword in overdue_keywords):
            overdue_tasks = get_employee_overdue_tasks(
                db=db,
                manager_id=manager_id,
                employee_id=employee.id
            )

            if not overdue_tasks:
                answer = f"{employee.name} has no overdue tasks."
            else:
                lines = [
                    f"OVERDUE TASKS FOR {employee.name.upper()}: "
                    f"{len(overdue_tasks)}"
                ]

                for task in overdue_tasks:
                    lines.extend([
                        "",
                        f"Task ID: {task['task_id']}",
                        f"Title: {task['title']}",
                        f"Description: {task['description']}",
                        f"Status: {task['status']}",
                        f"Priority: {task['priority']}",
                        f"Due date: {task['due_date']}"
                    ])

                answer = "\\n".join(lines)

            return {
                "answer": answer,
                "sources": []
            }

        # Handle other employee-specific questions through the SQL report.
        intent = detect_employee_intent(question)

        report = get_employee_targeted_report(
            db=db,
            manager_id=manager_id,
            employee_name=employee.name,
            intent=intent
        )

        if not report.get("found"):
            return {
                "answer": report.get(
                    "message",
                    "Employee report not found."
                ),
                "sources": []
            }

        answer = format_targeted_employee_report(report)

        return {
            "answer": answer,
            "sources": [
                {
                    "source_type": "employee_report",
                    "source_id": employee.id
                }
            ]
        }

    # 3. If no employee was named, handle team-level analytics.
    team_intent = detect_team_intent(question)

    if team_intent:
        answer = format_team_analytics(
            db=db,
            manager_id=manager_id,
            intent=team_intent
        )

        return {
            "answer": answer,
            "sources": []
        }
    
     # Use RAG when the question needs TaskFlow's stored knowledge.
    if should_use_rag(question):
        result = await ask_manager_question(
            db=db,
            manager_id=manager_id,
            question=question,
            top_k=5
        )

        return {
            "answer": result["answer"],
            "sources": result["sources"]
        }

    # Otherwise, use Ollama directly for general AI responses.
    system_message = """
    You are TaskFlow AI, an intelligent assistant for managers.

    You are powered by a local Llama 3.2 model.

    Help the manager with:
    - Productivity suggestions
    - Task planning and prioritization
    - Professional writing and drafting
    - Project management explanations
    - Meeting agendas
    - Brainstorming and creative ideas
    - General business recommendations
    - Learning and explanations

    Respond in a professional, friendly, and practical way.
    Use clear formatting and examples when helpful.

    Important rules:
    - Do not invent employee records or task statistics.
    - Do not claim to have accessed the TaskFlow database.
    - If asked for exact employee or task information,
    explain that this must be retrieved from TaskFlow's records.
    - Answer general knowledge and creative requests directly.
    """

    answer = await generate_response(
        user_message=question,
        system_message=system_message
    )

    return {
        "answer": answer,
        "sources": []
    }