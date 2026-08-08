import boto3
from pydantic import BaseModel

from app.core.approval_tokens import verify_approval_token, consume_token
from app.core.aws import BOTO_CONFIG
from app.core.logging import log

class RestartResult(BaseModel):
    success: bool
    detail: str

class ApprovalError(Exception):
    """Raised when a write action is attempted without a valid, unused approval token."""

async def restart_ecs_task(cluster: str, service: str, approval_token: str) -> RestartResult:
    claim = verify_approval_token(approval_token)
    
    if claim is None:
        log.warning("write_action_rejected", reason="invalid_token", action="restart_task")
        raise ApprovalError("token does not authorize this action")
    if claim.action != "restart_task":
        log.warning("write_action_rejected", reason="action_mismatch", action="restart_task")
        raise ApprovalError("token does not authorize this action")

    consumed = await consume_token(claim.jti)
    if not consumed:
        log.warning("write_action_rejected", reason="token_already_used", action="restart_task")
        raise ApprovalError("approval token already used")

    ecs = boto3.client("ecs", region_name="ap-south-1", config=BOTO_CONFIG)
    ecs.update_service(cluster=cluster, service=service, forceNewDeployment=True)

    log.info("write_action_executed", action="restart_task", incident_id=claim.incident_id,
             approved_by=claim.approved_by)
    return RestartResult(success=True, detail=f"Forced new deployment of {service}")