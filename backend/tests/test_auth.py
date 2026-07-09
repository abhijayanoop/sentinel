import pytest

from app.core.security import hash_password
from app.models.user import User


@pytest.mark.asyncio
async def test_login_success_and_protected_route(client, db_session_maker):
    async with db_session_maker() as session:
        session.add(User(email="you@example.com", hashed_password=hash_password("testpass123")))
        await session.commit()

    login = await client.post("/auth/login", json={"email": "you@example.com", "password": "testpass123"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    assert (await client.get("/incidents")).status_code == 401          # no token -> 401
    ok = await client.get("/incidents", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200                                        # with token -> 200


@pytest.mark.asyncio
async def test_login_wrong_password(client, db_session_maker):
    async with db_session_maker() as session:
        session.add(User(email="you@example.com", hashed_password=hash_password("correct")))
        await session.commit()

    resp = await client.post("/auth/login", json={"email": "you@example.com", "password": "wrong"})
    assert resp.status_code == 401