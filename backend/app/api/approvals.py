from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy import select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.core.logging import log
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.diagnosis import Diagnosis as DiagnosisModel
from app.core.approval_tokens import mint_approval_token
from app.core.queue import diagnosis_queue
from app.jobs.execute_action import execute_approved_action

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.post("/{incident_id}/approve")
async def approve_action(incident_id: int, current_user: str = Depends(get_current_user)):
    async with get_session() as session:
        approval = (await session.execute(select(Approval).where(Approval.incident_id == incident_id))).scalar_one_or_none()
        if approval is None:
            raise HTTPException(status_code=404, detail="no pending approval for this incident")
        if approval.status != "pending":
            raise HTTPException(status_code=409, detail=f"approval already {approval.status}")

        diagnosis = (await session.execute(
            select(DiagnosisModel).where(DiagnosisModel.incident_id == incident_id)
        )).scalar_one()

        action = "rollback_deploy" if "rollback" in (diagnosis.suggested_action or "").lower() else "restart_task"

        token, jti = mint_approval_token(incident_id, action, approved_by=current_user)
        approval.token_jti = jti
        approval.status = "approved"
        approval.approved_by = current_user
        approval.consumed = False

        session.add(AuditLog(
            incident_id=incident_id, actor=current_user, action="action_approved",
            detail={"action": action},
        ))
        await session.commit()

    diagnosis_queue.enqueue(execute_approved_action, incident_id, action, token)
    log.info("action_approved", incident_id=incident_id, approved_by=current_user, action=action)
    return {"status": "approved", "action": action}

@router.post("/{incident_id}/reject")
async def reject_action(incident_id: int, current_user: str = Depends(get_current_user)):
    async with get_session() as session:
        approval = (await session.execute(
            select(Approval).where(Approval.incident_id == incident_id)
        )).scalar_one_or_none()
        if approval is None:
            raise HTTPException(status_code=404, detail="no pending approval for this incident")
        if approval.status != "pending":
            raise HTTPException(status_code=409, detail=f"approval already {approval.status}")

        approval.status = "rejected"
        approval.approved_by = current_user
        approval.consumed = True          # a rejected token can never be used
        session.add(AuditLog(
            incident_id=incident_id, actor=current_user, action="action_rejected", detail={},
        ))
        await session.commit()

    log.info("action_rejected", incident_id=incident_id, rejected_by=current_user)
    return {"status": "rejected"}

