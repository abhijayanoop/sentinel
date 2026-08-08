"""Inspect jobs that failed after exhausting retries. Run this when something's wrong."""
from rq.registry import FailedJobRegistry

from app.core.queue import diagnosis_queue

registry = FailedJobRegistry(queue=diagnosis_queue)

if not registry.get_job_ids():
    print("No failed jobs.")
else:
    print(f"{len(registry.get_job_ids())} failed job(s):\n")
    for job_id in registry.get_job_ids():
        job = diagnosis_queue.fetch_job(job_id)
        if job is None:
            continue
        print(f"  id:     {job.id}")
        print(f"  func:   {job.func_name}{job.args}")
        print(f"  failed: {job.ended_at}")
        print(f"  error:  {(job.exc_info or '').strip().splitlines()[-1] if job.exc_info else 'unknown'}")
        print()
    print("To replay one:  rq requeue --queue diagnosis <job_id>")