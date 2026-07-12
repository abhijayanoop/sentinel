from pydantic import BaseModel
from sqlalchemy import select
from app.core.db import get_session
from app.models.incident_memory import IncidentMemory
from app.core.embedding import embed_text

class PastIncident(BaseModel):
    summary: str
    outcome: str | None
    similarity: float


class MemoryResult(BaseModel):
    matches: list[PastIncident]

async def search_past_incidents(query: str, limit:int = 5) -> MemoryResult:
    query_embedding = embed_text(query)
    async with get_session() as session:
        stmt = (
            select(
                IncidentMemory.summary, 
                IncidentMemory.outcome, 
                IncidentMemory.embedding.cosine_similiarity(query_embedding).label("distance")
            ).order_by("distance").limit(limit)
        )
        rows = (await session.execute(stmt)).all()

    matches = [
        PastIncident(summary=r.summary, outcome=r.outcome, similarity=round(1 - r.distance, 3))
        for r in rows
    ]
    return MemoryResult(matches=matches)