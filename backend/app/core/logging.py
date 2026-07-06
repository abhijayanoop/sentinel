import structlog
import logging

def configure_logging(log_level: str):
    logging.basicConfig(format="%(message)s", level=log_level)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),   # <- every log line becomes a JSON object
        ],
    )

log = structlog.get_logger()