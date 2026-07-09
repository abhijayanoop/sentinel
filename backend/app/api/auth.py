from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from app.schemas.auth import TokenResponse,LoginRequest
from app.core.db import get_session
from app.core.security import verify_password, create_access_token
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):    
    async with get_session() as session:
        result = await session.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return TokenResponse(access_token=create_access_token(subject=body.email))