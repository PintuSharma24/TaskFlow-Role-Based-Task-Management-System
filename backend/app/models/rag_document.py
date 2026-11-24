
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    func
)
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.database.base import Base


class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    source_id: Mapped[int] = mapped_column(
        nullable=False
    )

    manager_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    embedding = mapped_column(
        Vector(768),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index(
            "ix_rag_documents_source",
            "source_type",
            "source_id"
        ),
    )
