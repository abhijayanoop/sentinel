from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from app.core.db import Base

class RiskLevel(str, enum.Enum):
    low="low"
    medium="medium"
    high="high" 

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    raw_payload: Mapped[dict] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    diagnosis = relationship("Diagnosis", back_populates="incident", uselist=False)
    evidence = relationship("Evidence", back_populates="incident")

