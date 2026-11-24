
from pprint import pprint

from app.database.connection import SessionLocal
from app.services.employee_info_service import get_employee_report


def main():
    db = SessionLocal()

    try:
        manager_id = 3  # Neha Gupta

        employee_name = "Sneha"

        print("Testing Employee Information Retrieval...")
        print("Manager ID:", manager_id)
        print("Employee:", employee_name)

        report = get_employee_report(
            db=db,
            manager_id=manager_id,
            employee_name=employee_name
        )

        print("\nEMPLOYEE REPORT:")
        pprint(report, sort_dicts=False, width=100)

        if report["found"]:
            print("\nEMPLOYEE SUMMARY")
            print("Name:", report["employee"]["name"])
            print("Email:", report["employee"]["email"])
            print("Total Tasks:", report["task_statistics"]["total"])
            print("Completed:", report["task_statistics"]["completed"])
            print("Pending:", report["task_statistics"]["pending"])
            print("In Progress:", report["task_statistics"]["in_progress"])
            print(
                "Total Hours:",
                report["time_summary"]["total_hours_worked"]
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
