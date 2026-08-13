"""Reset demo state: clear incidents and restore the service. Run between demo runs."""

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.db import get_session
from sqlalchemy import text

from scripts.chaos import fix as restore_service


async def clear_data() -> None:
    async with get_session() as session:
        # order matters — clear children before parents (FK constraints)
        for table in (
            "audit_log",
            "approvals",
            "diagnoses",
            "incident_memory",
            "incidents",
        ):
            await session.execute(text(f"DELETE FROM {table}"))
        await session.commit()
    print("Cleared incidents, diagnoses, approvals, audit log, and memory.")


if __name__ == "__main__":
    print("Restoring service to healthy task definition...")
    restore_service()
    print("\nClearing demo data...")
    asyncio.run(clear_data())
    print("\nReady for a fresh demo run.")
