import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    DATABASE_URL: str = "sqlite:///./echomind.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
