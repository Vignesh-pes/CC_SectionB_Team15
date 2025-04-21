# app/core/config.py
import os # Import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    # Add TEST_DATABASE_URL, defaulting to None if not set
    TEST_DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()