from typing import Any, Callable
import json

from app.core.db import get_session
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.core.approval_tokens import mint_approval_token
from app.core.logging import log
from app.core.llm import llm, get_model
from app.agent.state import AgentState
from app.agent.prompts import SYNTHESIS_SYSTEM
from app.schemas.diagnosis import Diagnosis
from app.tools.read.deploys import get_recent_deploys
from app.tools.read.ecs_events import get_ecs_service_events
from app.tools.read.logs import get_cloudwatch_logs
from app.tools.read.memory import search_past_incidents
from app.tools.read.metrics import get_metric_data

READ_TOOLS: dict[str, Callable[..., Any]] = {
    "get_recent_deploys": get_recent_deploys,
    "get_metric_data": get_metric_data,
    "get_ecs_service_events": get_ecs_service_events,
    "get_cloudwatch_logs": get_cloudwatch_logs,
}

async def plan_and_gather(state: AgentState) -> AgentState:
    evidence_list: list[dict] = []

    try:
        memory = await search_past_incidents(state["incident_summary"])
        evidence_list.append({"tool_name": "search_past_incidents", "result": memory.model_dump()})
    except Exception as e:
        evidence_list.append({"tool_name": "search_past_incidents", "error": str(e)})

    for name, fn in READ_TOOLS.items():
        try:
            if name == "get_recent_deploys":
                result = fn()
            else:
                continue

            evidence_list.append({"tool_name": "get_recent_deploys", "result": result.model_dump()})
        except Exception as e:
            evidence_list.append({"tool_name": "get_recent_deploys", "error": str(e)})
    
    return {"evidence": evidence_list}

def synthesize_diagnosis(state: AgentState) -> AgentState:
    evidence_text = json.dumps(state.get("evidence", []), indent=2, default=str)
    diagnosis = llm.chat.completions.create(
        model=get_model(),
        response_model=Diagnosis,
        max_retries=2,
        messages=[
            {"role": "system", "content": SYNTHESIS_SYSTEM},
            {"role": "user", "content": f"Incident: {state['incident_summary']}\n\nEvidence:\n{evidence_text}"},
        ]
    )
    return {"diagnosis": diagnosis}

async def draft_action_and_request_approval(state: AgentState) -> AgentState:
    diagnosis = state["diagnosis"]
    incident_id = state["incident_id"]

    action = "restart_task"
    if "rollback" in (diagnosis.suggested_action or "").lower():
        action = "rollback_deploy"

    token, jti = mint_approval_token(incident_id, action, approved_by="pending")

    async with get_session() as session:
        session.add(Approval(
            incident_id=incident_id,
            token_jti=jti,
            status="pending",
            consumed=False,
        ))
        session.add(AuditLog(
            incident_id=incident_id, actor="agent", action="approval_requested",
            detail={"proposed_action": action, "risk_level": diagnosis.risk_level.value},
        ))
        await session.commit()

    log.info("approval_requested", incident_id=incident_id, action=action)
    return {}

async def escalate_high_risk(state: AgentState) -> AgentState:
    """For high-risk diagnoses: evidence only, no executable action, escalate to a human."""
    incident_id = state["incident_id"]
    async with get_session() as session:
        session.add(AuditLog(
            incident_id=incident_id, actor="agent", action="escalated_high_risk",
            detail={"reason": "risk_level=high; no auto-action drafted"},
        ))
        await session.commit()
    log.info("incident_escalated", incident_id=incident_id, reason="high_risk")
    return {}

def route_on_risk(state: AgentState) -> str:
    """Conditional-edge function: decide the next node based on the diagnosis risk."""
    diagnosis = state["diagnosis"]
    if diagnosis.risk_level.value == "high":
        return "escalate_high_risk"
    return "draft_action_and_request_approval"
