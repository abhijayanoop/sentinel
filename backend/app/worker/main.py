import sys
from rq import SimpleWorker, Worker
from app.core.queue import redis_conn

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

WorkerClass = SimpleWorker if sys.platform == "win32" else Worker

if __name__ == "__main__":
    worker = WorkerClass(["diagnosis"], connection=redis_conn)
    worker.work(with_scheduler=True)