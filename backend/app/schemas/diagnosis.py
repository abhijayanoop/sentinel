from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class EvidenceRef(BaseModel):
    tool_name: str = Field(description="Which diagnostic tool produced this evidence")
    summary: str = Field(description="One-sentence summary of what this evidence showed")


class Diagnosis(BaseModel):
    root_cause_hypothesis: str = Field(
        description="The single most likely root cause, stated plainly in one or two sentences."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="How confident you are in this hypothesis, from 0.0 to 1.0.",
    )
    risk_level: RiskLevel = Field(
        description="How risky the suggested remediation would be to execute automatically. "
                    "low = safe reversible action (e.g. restart a stateless task). "
                    "high = destructive or hard-to-reverse (e.g. rollback, scale down DB)."
    )
    suggested_action: str | None = Field(
        default=None,
        description="A concrete recommended action, or null if the risk is high and a human "
                    "should decide with no auto-suggested action.",
    )
    evidence: list[EvidenceRef] = Field(
        default_factory=list,
        description="The pieces of evidence that support this hypothesis.",
    )