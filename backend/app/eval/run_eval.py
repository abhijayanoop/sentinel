import asyncio
import json
import sys
import uuid
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.agent.graph import agent_graph
from app.core.db import get_session
from app.models.incident import Incident

DATA = Path(__file__).parent / "incidents.json"


async def _create_eval_incident(summary: str) -> int:
    async with get_session() as session:
        incident = Incident(
            source="eval",
            idempotency_key=f"eval-{uuid.uuid4()}",
            raw_payload={"summary": summary},
        )
        session.add(incident)
        await session.commit()
        await session.refresh(incident)
        return incident.id


async def evaluate() -> dict:
    cases = json.loads(DATA.read_text())
    root_cause_hits = 0
    risk_hits = 0

    for case in cases:
        incident_id = await _create_eval_incident(case["summary"])
        result = await agent_graph.ainvoke({
            "incident_id": incident_id,
            "incident_summary": case["summary"],
            "evidence": [],
        })
        diag = result["diagnosis"]
        text = diag.root_cause_hypothesis.lower()

        if any(kw.lower() in text for kw in case["expected_root_cause_keywords"]):
            root_cause_hits += 1
        if diag.risk_level.value == case["expected_risk"]:
            risk_hits += 1

    n = len(cases)
    return {
        "cases": n,
        "root_cause_accuracy": round(root_cause_hits / n, 3),
        "risk_accuracy": round(risk_hits / n, 3),
    }


if __name__ == "__main__":
    scores = asyncio.run(evaluate())
    print(json.dumps(scores, indent=2))
    if scores["root_cause_accuracy"] < 0.6:
        raise SystemExit(f"Root-cause accuracy {scores['root_cause_accuracy']} below threshold 0.6")