import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.db import get_session
from app.core.security import hash_password
from app.models.user import User

async def main(email: str, password: str) -> None:
    async with get_session() as session:
        session.add(User(email=email, hashed_password=hash_password(password)))
        await session.commit()
    print(f"created user: {email}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python -m scripts.create_user <email> <password>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
