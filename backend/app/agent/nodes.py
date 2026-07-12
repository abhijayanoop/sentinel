import json
from app.core.llm import llm, get_model
from app.agent.state import AgentState
from app.agent.prompts import PLANNER_SYSTEM, SYNTHESIS_SYSTEM
from app.schemas.diagnosis import Diagnosis
from app.tools.read.deploys import get_recent_deploys
from app.tools.read.ecs_events import get_ecs_service_events
from app.tools.read.logs import get_cloudwatch_logs
from app.tools.read.memory import search_past_incidents
from app.tools.read.metrics import get_metric_data

READ_TOOLS = {
    "get_recent_deploys": get_recent_deploys,
    "get_metric_data": get_metric_data,
    "get_ecs_service_events": get_ecs_service_events,
    "get_cloudwatch_logs": get_cloudwatch_logs,
}

async def plan_and_gather(state: AgentState) -> AgentState:
    evidence_list: list[str] = []

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
