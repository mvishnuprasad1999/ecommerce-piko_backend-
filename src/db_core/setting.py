# from pydantic_settings import BaseSettings,SettingsConfigDict

# class Settings(BaseSettings):
#     model_config=SettingsConfigDict(env_file=".env",extra="ignore")
#     DB_CONNECTION:str

# setup=Settings()

# src/db_core/setting.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # Use this locally
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )
    
    # These will be read from:
    # 1. .env file (local development)
    # 2. Render environment variables (production)
    DB_CONNECTION: str = os.getenv("DATABASE_URL", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Optional
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

setup = Settings()