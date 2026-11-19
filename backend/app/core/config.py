"""
IntelliGrievance AI - Application Configuration & Settings
Environment-based configuration with Pydantic Settings.
Supports PostgreSQL with transparent SQLite zero-config development fallback.
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "IntelliGrievance AI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Security & Tokens
    SECRET_KEY: str = os.getenv("SECRET_KEY", "b49a5b3e94fd89d2d0c24c29cf47b7ee11a567ecb23e59049280d0d8664bb520")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # Database
    # Defaults to local SQLite if DATABASE_URL is not provided or points to unconfigured Postgres
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'intelligrievance.db'))}"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    class Config:
        case_sensitive = True

settings = Settings()
