
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TaskHistory(Base):
    __tablename__ = "task_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=False
    )

    changed_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    old_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    new_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    old_assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    new_assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    task = relationship(
        "Task",
        back_populates="history"
    )

    changed_by = relationship(
        "User",
        back_populates="task_history",
        foreign_keys=[changed_by_id]
    )

    old_assignee = relationship(
        "User",
        foreign_keys=[old_assignee_id]
    )

    new_assignee = relationship(
        "User",
        foreign_keys=[new_assignee_id]
    )
