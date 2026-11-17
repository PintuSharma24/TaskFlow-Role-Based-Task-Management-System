from getpass import getpass

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.core.security import verify_password
from app.models.user import User


email = input("Enter Admin email: ").strip().lower()
password = getpass("Enter Admin password: ")

db = SessionLocal()

try:
    admin = db.scalar(
        select(User).where(
            User.email == email,
            User.role == "admin"
        )
    )

    if admin is None:
        print("\nAdmin account: NOT FOUND")
    else:
        print("\nAdmin account: FOUND")
        print("User ID:", admin.id)
        print("Role:", admin.role)
        print("Active:", admin.is_active)

        password_matches = verify_password(
            password,
            admin.password_hash
        )

        print("Password matches:", password_matches)

finally:
    db.close()
