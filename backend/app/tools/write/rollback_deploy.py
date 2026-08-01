import boto3
from pydantic import BaseModel

from app.core.approval_tokens import verify_approval_token, consume_token
from app.core.logging import log
from app.tools.write.restart_task import ApprovalError


class RollbackResult(BaseModel):
    success: bool
    detail: str
    rolled_back_to: str | None


async def rollback_deploy(cluster: str, service: str, approval_token: str) -> RollbackResult:
    claims = verify_approval_token(approval_token)
    if claims is None or claims.action != "rollback_deploy":
        log.warning("write_action_rejected", reason="invalid_or_mismatched_token", action="rollback_deploy")
        raise ApprovalError("invalid, expired, or mismatched approval token")

    consumed = await consume_token(claims.jti)
    if not consumed:
        log.warning("write_action_rejected", reason="token_already_used", action="rollback_deploy")
        raise ApprovalError("approval token already used")

    ecs = boto3.client("ecs", region_name="ap-south-1")

    svc = ecs.describe_services(cluster=cluster, services=[service])["services"][0]
    current_td_arn = svc["taskDefinition"]
    family = current_td_arn.split("/")[-1].split(":")[0]
    current_rev = int(current_td_arn.split(":")[-1])

    if current_rev <= 1:
        raise ApprovalError("no previous revision to roll back to")

    previous = f"{family}:{current_rev - 1}"
    ecs.update_service(cluster=cluster, service=service, taskDefinition=previous)

    log.info("write_action_executed", action="rollback_deploy", incident_id=claims.incident_id,
             approved_by=claims.approved_by, rolled_back_to=previous)
    return RollbackResult(success=True, detail=f"Rolled {service} back", rolled_back_to=previous)