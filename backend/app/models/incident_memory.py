from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.db import Base
from app.models.incident import utcnow


class IncidentMemory(Base):
    __tablename__ = "incident_memory"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"))
    summary: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))  
    outcome: Mapped[str | None] = mapped_column(String, nullable=True)  # fixed|not_fixed|false_positive
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)