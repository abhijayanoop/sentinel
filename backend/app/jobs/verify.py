import asyncio
from datetime import datetime, timedelta, timezone

import boto3
from botocore.config import Config
from sqlalchemy import select

from app.core.db import get_session
from app.core.embedding import embed_text
from app.core.logging import log
from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.incident_memory import IncidentMemory

BOTO_CONFIG = Config(connect_timeout=5, read_timeout=15, retries={"max_attempts": 2})

CLUSTER = "sentinel-cluster"
SERVICE = "sentinel-backend-service"


async def _check_resolution(incident_id: int) -> str:
    ecs = boto3.client("ecs", region_name="ap-south-1", config=BOTO_CONFIG)

    # poll for up to 3 minutes — a rollback takes time to take effect
    deadline = datetime.now(timezone.utc) + timedelta(minutes=3)
    while datetime.now(timezone.utc) < deadline:
        try:
            svc = ecs.describe_services(cluster=CLUSTER, services=[SERVICE])[
                "services"
            ][0]
            running, desired = svc["runningCount"], svc["desiredCount"]
            log.info(
                "verification_poll",
                incident_id=incident_id,
                running=running,
                desired=desired,
            )
            if running >= desired and desired > 0:
                return "fixed"
        except Exception as e:
            log.warning(
                "verification_check_failed", incident_id=incident_id, error=str(e)
            )
        await asyncio.sleep(15)

    log.info("verification_timed_out", incident_id=incident_id)
    return "not_fixed"


async def verify_and_record(incident_id: int, action: str) -> None:
    await asyncio.sleep(30)

    outcome = await _check_resolution(incident_id)

    async with get_session() as session:
        incident = (
            await session.execute(select(Incident).where(Incident.id == incident_id))
        ).scalar_one()
        incident.status = "resolved" if outcome == "fixed" else "action_failed"

        session.add(
            AuditLog(
                incident_id=incident_id,
                actor="agent",
                action="verification_completed",
                detail={"outcome": outcome, "action": action},
            )
        )

        summary = f"Incident {incident_id}: action '{action}' resulted in '{outcome}'."
        session.add(
            IncidentMemory(
                incident_id=incident_id,
                summary=summary,
                embedding=embed_text(summary),
                outcome=outcome,
            )
        )
        await session.commit()

    log.info("verification_completed", incident_id=incident_id, outcome=outcome)
