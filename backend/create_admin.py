
from getpass import getpass

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def create_admin():
    db = SessionLocal()

    try:
        # Check whether an Admin already exists
        existing_admin = db.scalar(
            select(User).where(User.role == "admin")
        )

        if existing_admin:
            print("An Admin account already exists.")
            print(f"Admin email: {existing_admin.email}")
            return

        print("\n=== Create Initial Admin Account ===")

        name = input("Enter Admin name: ").strip()
        email = input("Enter Admin email: ").strip().lower()

        password = getpass("Enter Admin password: ")
        confirm_password = getpass("Confirm Admin password: ")

        # Validate inputs
        if not name or not email:
            print("Name and email are required.")
            return

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        # Check whether email is already registered
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            print("This email is already registered.")
            return

        # Hash password using Argon2
        hashed_password = hash_password(password)

        # Create Admin account
        admin = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            role="admin",
            is_active=True,
            manager_id=None
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nAdmin account created successfully!")
        print(f"Admin ID: {admin.id}")
        print(f"Admin Name: {admin.name}")
        print(f"Admin Email: {admin.email}")
        print(f"Admin Role: {admin.role}")

    except Exception:
        db.rollback()
        print("An error occurred while creating the Admin account.")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
