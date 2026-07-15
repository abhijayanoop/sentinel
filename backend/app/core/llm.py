import instructor
from openai import OpenAI
from app.core.config import settings

if settings.langfuse_public_key and settings.langfuse_secret_key:
    # from app.core import tracing 
    from langfuse.openai import OpenAI as TracedOpenAI
    _openai_client = TracedOpenAI(api_key=settings.openai_api_key)
else:
    _openai_client = OpenAI(api_key=settings.openai_api_key)

llm = instructor.from_openai(_openai_client)

def get_model() -> str:
    return settings.openai_model