from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.api.deps import get_current_user
from app.core.db import get_session
from app.models import Incident

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("")
async def list_incidents(current_user: str = Depends(get_current_user)):
    async with get_session() as session:
        result = await session.execute(select(Incident).order_by(Incident.created_at.desc()).limit(50))
        incidents = result.scalars().all()

    return [{"id": i.id, "source": i.source, "status": i.status, "created_at": i.created_at.isoformat()} for i in incidents]