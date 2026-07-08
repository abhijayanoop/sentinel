from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models.incident import utcnow


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), unique=True)
    token_jti: Mapped[str] = mapped_column(String, unique=True, index=True)  
    status: Mapped[str] = mapped_column(String, default="pending")           
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False)           
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    incident: Mapped["Incident"] = relationship(back_populates="approval")