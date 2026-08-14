import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager
from typing import cast
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging, log
from app.api import health, webhooks, auth, incidents, approvals
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter

configure_logging(settings.log_level)

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("app_startup", environment=settings.environment)
    yield
    log.info("app_shutdown")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# lets the locally-run frontend (Vite dev server) call the deployed AWS API
# directly, bypassing Vite's dev proxy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(webhooks.router)
app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(approvals.router)
app.state.limiter = limiter


def _handle_rate_limit_exceeded(request: Request, exc: Exception) -> Response:
    """Adapts slowapi's RateLimitExceeded-typed handler to the Exception-typed
    signature FastAPI's add_exception_handler expects."""
    return _rate_limit_exceeded_handler(request, cast(RateLimitExceeded, exc))


app.add_exception_handler(RateLimitExceeded, _handle_rate_limit_exceeded)