import asyncio

from app.core.db import get_session
from app.core.logging import log
from app.models.audit_log import AuditLog
from app.tools.write.restart_task import restart_ecs_task, RestartResult, ApprovalError
from app.tools.write.rollback_deploy import rollback_deploy, RollbackResult
from app.jobs.verify import verify_and_record

DEMO_CLUSTER = "sentinel-cluster"
DEMO_SERVICE = "sentinel-backend-service"


def execute_approved_action(incident_id: int, action: str, token: str) -> None:
    asyncio.run(_execute_async(incident_id, action, token))


async def _execute_async(incident_id: int, action: str, token: str) -> None:
    log.info("execution_started", incident_id=incident_id, action=action)
    result: RestartResult | RollbackResult
    try:
        if action == "restart_task":
            result = await restart_ecs_task(DEMO_CLUSTER, DEMO_SERVICE, token)
        elif action == "rollback_deploy":
            result = await rollback_deploy(DEMO_CLUSTER, DEMO_SERVICE, token)
        else:
            raise ApprovalError(f"unknown action: {action}")
    except ApprovalError as e:
        async with get_session() as session:
            session.add(AuditLog(
                incident_id=incident_id, actor="system", action="execution_rejected",
                detail={"reason": str(e), "action": action},
            ))
            await session.commit()
        log.warning("execution_rejected", incident_id=incident_id, reason=str(e))
        return
    except Exception as e:
        async with get_session() as session:
            session.add(AuditLog(
                incident_id=incident_id, actor="system", action="execution_failed",
                detail={"reason": str(e), "action": action},
            ))
            await session.commit()
        log.error("execution_failed", incident_id=incident_id, action=action, error=str(e))
        return

    async with get_session() as session:
        session.add(AuditLog(
            incident_id=incident_id, actor="agent", action="action_executed",
            detail={"action": action, "detail": result.detail},
        ))
        await session.commit()

    log.info("execution_completed", incident_id=incident_id, action=action)

    await verify_and_record(incident_id, action)