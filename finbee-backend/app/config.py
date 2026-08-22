"""
Application configuration.
Loads all settings from environment variables (.env in local dev).
Never hardcode secrets here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FinBee Backend"
    ENV: str = "development"  # development | production
    DEBUG: bool = True

    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "financial_planning_db"

    # Auth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI provider (abstracted — swap without touching business logic)
    AI_PROVIDER: str = "groq"  # groq | huggingface
    AI_MODEL: str = ""
    AI_API_KEY: str = ""

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
