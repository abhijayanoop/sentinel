import uuid
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.db import get_session
from app.models.approval import Approval

APPROVAL_TOKEN_EXPIRE_MINUTES = 15

class ApprovalClaims(BaseModel):
    incident_id: int
    action: str
    jti: str
    approved_by: str

def mint_approval_token(incident_id: int, action: str, approved_by: str) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=APPROVAL_TOKEN_EXPIRE_MINUTES)
    payload = {
        "incident_id": incident_id,
        "action": action,
        "jti": jti,
        "approved_by": approved_by,
        "exp": expire,
        "purpose": "sentinel-approval",
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token, jti

def verify_approval_token(token: str) -> ApprovalClaims | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError:
        return None
    
    if payload.get("purpose") != "sentinel-approval":
        return None  
    
    try:
        return ApprovalClaims(
            incident_id=payload["incident_id"],
            action=payload["action"],
            jti=payload["jti"],
            approved_by=payload["approved_by"],
        )
    except KeyError:
        return None
    
async def consume_token(jti: str) -> bool:
    async with get_session() as session:
        approval = (await session.execute(
            select(Approval).where(Approval.token_jti == jti).with_for_update())
            ).scalar_one_or_none()
        
        if approval is None or approval.consumed:
            return False
        
        approval.consumed = True
        approval.status = "used"
        await session.commit()
        return True

