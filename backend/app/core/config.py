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
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()