from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "sentinel"
    environment: str = "local"         
    log_level: str = "INFO"
    database_url: str
    webhook_secret: str                  
    jwt_secret: str                      
    jwt_expire_minutes: int = 60
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    github_token: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()