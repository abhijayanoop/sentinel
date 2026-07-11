from __future__ import annotations
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.diagnosis import Diagnosis
    from app.models.evidence import Evidence
    from app.models.approval import Approval

class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)          # "cloudwatch", "github", ...
    idempotency_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    raw_payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    diagnosis: Mapped["Diagnosis | None"] = relationship(back_populates="incident", uselist=False)
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="incident")
    approval: Mapped["Approval | None"] = relationship(back_populates="incident", uselist=False)