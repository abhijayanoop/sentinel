import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import configure_logging, log
from app.api import health

configure_logging(settings.log_level)

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("app_startup", environment=settings.environment)
    yield
    log.info("app_shutdown")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health.router)