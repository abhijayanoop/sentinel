from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.db import Base

class AuditLog(Base):
    id: Mapped[str] = mapped_column(String, primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"))
    actor: Mapped[str] = mapped_column(String)      # "agent" or a user's email
    action: Mapped[str] = mapped_column(String)      # "diagnosis_created", "action_approved", "task_restarted"
    detail: Mapped[dict] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)