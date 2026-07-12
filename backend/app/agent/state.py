from typing import TypedDict
from app.schemas.diagnosis import Diagnosis

class AgentState(TypedDict, total=False):
    incident_id: str
    incident_summary: str
    evidence: list[dict]
    diagnosis: Diagnosis | None
    error: str | None