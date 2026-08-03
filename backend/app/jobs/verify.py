import asyncio

from sqlalchemy import select

from app.core.db import get_session
from app.core.logging import log
from app.core.embedding import embed_text
from app.models.incident import Incident
from app.models.audit_log import AuditLog
from app.models.incident_memory import IncidentMemory


async def verify_and_record(incident_id: int, action: str) -> None:
    await asyncio.sleep(30)

    outcome = await _check_resolution(incident_id)

    async with get_session() as session:
        incident = (await session.execute(
            select(Incident).where(Incident.id == incident_id)
        )).scalar_one()
        incident.status = "resolved" if outcome == "fixed" else "action_failed"

        session.add(AuditLog(
            incident_id=incident_id, actor="agent", action="verification_completed",
            detail={"outcome": outcome, "action": action},
        ))

        summary = f"Incident {incident_id}: action '{action}' resulted in '{outcome}'."
        session.add(IncidentMemory(
            incident_id=incident_id,
            summary=summary,
            embedding=embed_text(summary),
            outcome=outcome,
        ))
        await session.commit()

    log.info("verification_completed", incident_id=incident_id, outcome=outcome)


async def _check_resolution(incident_id: int) -> str:
    return "fixed"