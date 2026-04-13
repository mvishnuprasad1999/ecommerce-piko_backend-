# from pydantic_settings import BaseSettings,SettingsConfigDict

# class Settings(BaseSettings):
#     model_config=SettingsConfigDict(env_file=".env",extra="ignore")
#     DB_CONNECTION:str

# setup=Settings()

# src/db_core/setting.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )
    
    DB_CONNECTION: str = ""
    GROQ_API_KEY: str = ""
    CLOUDINARY_API_KEY_SECRET: str = ""
    CLOUDINARY_APIKEY: str = ""
    CLOUDINARY_NAME: str = ""

setup = Settings()