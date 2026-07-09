import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.logging import log
from app.core.db import get_session
from app.models.incident import Incident

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def verify_signature(raw_body: bytes, signature_header: str) -> bool:
    expected = hmac.new(settings.webhook_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)

@router.post("/cloudwatch")
async def cloudwatch_webhook(request: Request):
    raw_body = await request.body()
    signature_header = request.headers.get("X-Signature", "")

    if not verify_signature(raw_body, signature_header):
        log.warning("webhook_invalid_signature", source="cloudwatch")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid signature")
    
    payload = await request.json()
    try:
        idempotency_key = f"{payload["alarmId"]}:{payload["stateChangeTime"]}"
    except KeyError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "missing alarmId or stateChangeTime")
    
    async with get_session() as session:
        incident = Incident(source="cloudwatch", idempotency_key=idempotency_key, raw_payload=payload)
        session.add(incident)
        try:
            await session.commit()
            await session.refresh(incident)
        except IntegrityError:
            await session.rollback()
            log.info("webhook_duplicate_ignored", idempotency_key=idempotency_key)
            return {"status": "duplicate_ignored"}

    log.info("incident_created", incident_id=incident.id, source="cloudwatch")
    return {"status": "accepted", "incident_id": incident.id}