
from datetime import date, datetime

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Date,
    DateTime,
    CheckConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed')",
            name="check_task_status"
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="check_task_priority"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    assigned_to_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    created_by = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[created_by_id]
    )

    assigned_to = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assigned_to_id]
    )

    history = relationship(
        "TaskHistory",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    time_logs = relationship(
        "TimeLog",
        back_populates="task"
    )
