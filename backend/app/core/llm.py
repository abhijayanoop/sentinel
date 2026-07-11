import instructor
from openai import OpenAI
from app.core.config import settings

_openai_client = OpenAI(api_key=settings.openai_api_key)

llm = instructor.from_openai(_openai_client)

def get_model() -> str:
    return settings.openai_model