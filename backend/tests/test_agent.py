from contextlib import asynccontextmanager

import pytest

from app.schemas.diagnosis import Diagnosis, RiskLevel


@pytest.mark.asyncio
async def test_agent_produces_diagnosis(monkeypatch, db_session_maker):
    fake = Diagnosis(root_cause_hypothesis="memory exhaustion after deploy",
                     confidence=0.85, risk_level=RiskLevel.high)

    # patch synthesis to avoid a real LLM call in CI
    import app.agent.nodes as nodes
    import app.agent.graph as graph_module
    def fake_synth(state):
        return {"diagnosis": fake}
    monkeypatch.setattr(nodes, "synthesize_diagnosis", fake_synth)
    monkeypatch.setattr(graph_module, "synthesize_diagnosis", fake_synth)

    # patch memory search to avoid needing a DB/embeddings in this unit test
    async def fake_mem(*a, **k):
        from app.tools.read.memory import MemoryResult
        return MemoryResult(matches=[])
    monkeypatch.setattr(nodes, "search_past_incidents", fake_mem)

    # patch the DB session so escalate_high_risk/draft_action don't hit real Postgres
    @asynccontextmanager
    async def override_get_session():
        async with db_session_maker() as session:
            yield session
    monkeypatch.setattr(nodes, "get_session", override_get_session)

    from app.agent.graph import build_graph
    graph = build_graph()
    result = await graph.ainvoke({"incident_id": 1, "incident_summary": "test", "evidence": []})
    assert result["diagnosis"].confidence == 0.85