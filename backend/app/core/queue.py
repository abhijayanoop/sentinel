from redis import Redis
from rq import Queue, Retry

from app.core.config import settings

redis_conn = Redis.from_url(settings.redis_url)

diagnosis_queue = Queue("diagnosis", connection=redis_conn, default_timeout=300)

DEFAULT_RETRY = Retry(max=3, interval=[10, 60, 180])