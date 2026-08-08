import asyncio
import signal
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from rq import Worker

from app.core.logging import log
from app.core.queue import diagnosis_queue, redis_conn


def main() -> None:
    worker = Worker([diagnosis_queue], connection=redis_conn)

    def handle_sigterm(signum, frame):
        log.info("worker_shutdown_requested", signal=signum)
        worker.request_stop(signum, frame)

    signal.signal(signal.SIGTERM, handle_sigterm)
    log.info("worker_started")
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()