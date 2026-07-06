from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import configure_logging, log
from app.api import health

configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.include_router(health.router)

@app.on_event("startup")
async def on_startup():
    log.info("app_startup", environment=settings.environment)