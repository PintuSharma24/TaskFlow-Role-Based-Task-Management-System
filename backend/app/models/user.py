
from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    CheckConstraint,
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'manager', 'employee')",
            name="check_user_role"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    role: Mapped[str] = mapped_column(String(20), nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    manager = relationship(
        "User",
        remote_side="User.id",
        back_populates="team_members"
    )

    team_members = relationship(
        "User",
        back_populates="manager"
    )

    created_tasks = relationship(
        "Task",
        back_populates="created_by",
        foreign_keys="Task.created_by_id"
    )

    assigned_tasks = relationship(
        "Task",
        back_populates="assigned_to",
        foreign_keys="Task.assigned_to_id"
    )

    task_history = relationship(
        "TaskHistory",
        back_populates="changed_by",
        foreign_keys="TaskHistory.changed_by_id"
    )

    time_logs = relationship(
        "TimeLog",
        back_populates="employee"
    )
