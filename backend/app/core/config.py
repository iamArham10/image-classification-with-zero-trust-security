"""
This file contains env configurations for the application
"""
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os
from typing import List

# Create path for .env file
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'

# Create path for .env file
load_dotenv(dotenv_path=ENV_PATH)

# Define Settings class using Pydantic
class Settings(BaseSettings):
    # Admin settings
    ADMIN_CREATION_TOKEN: str
    ALLOWED_ADMIN_CREATION_HOSTS: List[str] 

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Database settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # Session settings
    REQUESTS_PER_MINUTES: int

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{SELF.DB_HOST}:{SELF.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ENV_PATH
        case_sensitive = True

settings = Settings()
