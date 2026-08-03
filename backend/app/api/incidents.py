from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.api.deps import get_current_user
from app.core.db import get_session
from app.models import Incident
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.diagnosis import Diagnosis as DiagnosisModel

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("")
async def list_incidents(current_user: str = Depends(get_current_user)):
    async with get_session() as session:
        result = await session.execute(select(Incident).order_by(Incident.created_at.desc()).limit(50))
        incidents = result.scalars().all()

    return [{"id": i.id, "source": i.source, "status": i.status, "created_at": i.created_at.isoformat()} for i in incidents]

@router.get("/{incident_id}")
async def list_by_id(incident_id: int, current_user: str = Depends(get_current_user)):
    async with get_session() as session:
        incident = (await session.execute(select(Incident).where(Incident.id == incident_id))).scalar_one_or_none()
        if incident is None:
            raise HTTPException(status_code=404, detail="incident not found")

        diagnosis = (await session.execute(
            select(DiagnosisModel).where(DiagnosisModel.incident_id == incident_id)
        )).scalar_one_or_none()
        approval = (await session.execute(
            select(Approval).where(Approval.incident_id == incident_id)
        )).scalar_one_or_none()
        audit = (await session.execute(
            select(AuditLog).where(AuditLog.incident_id == incident_id).order_by(AuditLog.created_at)
        )).scalars().all()

        return {
        "id": incident.id,
        "source": incident.source,
        "status": incident.status,
        "created_at": incident.created_at.isoformat(),
        "diagnosis": None if diagnosis is None else {
            "root_cause_hypothesis": diagnosis.root_cause_hypothesis,
            "confidence": diagnosis.confidence,
            "risk_level": diagnosis.risk_level,
            "suggested_action": diagnosis.suggested_action,
            "evidence_refs": diagnosis.evidence_refs,
        },
        "approval": None if approval is None else {
            "status": approval.status, "approved_by": approval.approved_by,
        },
        "audit_log": [{"actor": a.actor, "action": a.action, "detail": a.detail,
                       "created_at": a.created_at.isoformat()} for a in audit],
    }