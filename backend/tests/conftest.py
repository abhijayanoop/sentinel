from contextlib import asynccontextmanager

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.db import Base
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session_maker():
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,   # one shared in-memory DB for the test's lifetime
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    yield maker
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session_maker):
    @asynccontextmanager
    async def override_get_session():
        async with db_session_maker() as session:
            yield session

    # point each route module's get_session at the test DB
    import app.api.webhooks as webhooks_module
    import app.api.auth as auth_module
    import app.api.incidents as incidents_module
    import app.api.approvals as approvals_module
    for mod in (webhooks_module, auth_module, incidents_module, approvals_module):
        mod.get_session = override_get_session

    # background tasks run in-process (and synchronously, under the ASGI test
    # transport) — stub out the agent pipeline so route tests don't make real
    # LLM/AWS calls or touch the real dev database via app/jobs' own get_session
    async def _noop(*args, **kwargs):
        pass

    webhooks_module.run_diagnosis_async = _noop
    approvals_module.execute_approved_action_async = _noop

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac