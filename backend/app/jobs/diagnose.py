import asyncio
from sqlalchemy import select
from app.core.db import get_session
from app.core.logging import log
from app.agent.graph import agent_graph
from app.models.incident import Incident
from app.models.diagnosis import Diagnosis as DiagnosisModel
from app.models.audit_log import AuditLog

def run_diagnosis(incident_id: int) -> None:
    asyncio.run(_run_diagnosis_async(incident_id))

async def _run_diagnosis_async(incident_id: int) -> None:
    async with get_session() as session:
        incident = (await session.execute(
            select(Incident).where(Incident.id == incident_id)
        )).scalar_one_or_none()

        if incident is None:
            log.warning("diagnosis_incident_not_found", incident_id=incident_id)
            return
        
    summary = _summarize_payload(incident.raw_payload)

    log.info("Diagnosis started", incident_id=incident_id)

    result = await agent_graph.ainvoke({
        "incident_id": incident_id,
        "incident_summary": summary,
        "evidence": [],
    })

    diagnosis = result["diagnosis"]

    async with get_session() as session:
        session.add(DiagnosisModel(
            incident_id=incident_id,
            root_cause_hypothesis=diagnosis.root_cause_hypothesis,
            confidence=diagnosis.confidence,
            risk_level=diagnosis.risk_level.value,
            suggested_action=diagnosis.suggested_action,
            evidence_refs={"evidence": [e.model_dump() for e in diagnosis.evidence]},
        ))
        session.add(AuditLog(
            incident_id=incident_id,
            actor="agent",
            action="diagnosis_created",
            detail={"confidence": diagnosis.confidence, "risk_level": diagnosis.risk_level.value},
        ))
        incident.status = "diagnosed"
        await session.commit()
    
    log.info("diagnosis_completed", incident_id=incident_id,
             confidence=diagnosis.confidence, risk_level=diagnosis.risk_level.value)


def _summarize_payload(payload: dict) -> str:
    parts = []
    if "alarmId" in payload:
        parts.append(f"Alarm: {payload['alarmId']}")
    if "newStateReason" in payload:
        parts.append(f"Reason: {payload['newStateReason']}")
    if "trigger" in payload:
        parts.append(f"Trigger: {payload['trigger']}")
    return " | ".join(parts) if parts else str(payload)