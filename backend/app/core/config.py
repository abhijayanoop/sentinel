from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "sentinel"
    environment: str = "local"  
    # database_url: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env"        

settings = Settings()