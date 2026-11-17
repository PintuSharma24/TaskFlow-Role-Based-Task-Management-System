
from datetime import date, datetime

from sqlalchemy import (
    ForeignKey,
    Date,
    DateTime,
    Numeric,
    Text,
    CheckConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TimeLog(Base):
    __tablename__ = "time_logs"

    __table_args__ = (
        CheckConstraint(
            "hours_worked > 0",
            name="check_positive_hours"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=False
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    hours_worked: Mapped[float] = mapped_column(
        Numeric(7, 2),
        nullable=False
    )

    work_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    task = relationship(
        "Task",
        back_populates="time_logs"
    )

    employee = relationship(
        "User",
        back_populates="time_logs"
    )
