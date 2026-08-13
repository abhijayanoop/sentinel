from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "sentinel"
    environment: str = "local"
    log_level: str = "INFO"
    database_url: str | None = None
    database_host: str | None = None
    database_port: int = 5432
    database_name: str = "sentinel"
    database_user: str = "sentinel_admin"
    db_password: str | None = None
    webhook_secret: str
    jwt_secret: str                      
    jwt_expire_minutes: int = 60
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    github_token: str | None = None
    github_repo: str = "octocat/Hello-World"
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        """DATABASE_URL if set directly, else assembled from the split DATABASE_* + DB_PASSWORD vars (used in ECS, where the password comes from Secrets Manager)."""
        if self.database_url:
            return self.database_url
        if self.database_host and self.db_password:
            return (
                f"postgresql+psycopg://{self.database_user}:{self.db_password}"
                f"@{self.database_host}:{self.database_port}/{self.database_name}"
            )
        raise ValueError(
            "Set DATABASE_URL, or DATABASE_HOST together with DB_PASSWORD"
        )


settings = Settings()