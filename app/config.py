from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    
    # Redis
    REDIS_URL: str
    
    # User Service
    USER_SERVICE_URL: str = "http://user-service:8001"
    
    # Face Engine
    FACE_MODEL: str
    SIMILARITY_THRESHOLD: float = 0.60
    MIN_QUALITY_SCORE: float = 0.50
    RECOGNITION_RATE_LIMIT: str = "10/minute"
    
    # Adaptive Routing
    CPU_THRESHOLD: float = 60.0
    QUEUE_THRESHOLD: int = 20
    
    # Minio / S3 Storage
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_BUCKET: str
    AWS_ENDPOINT: str
    
    # App
    API_KEY: str
    APP_ENV: str = "development"
    BASE_PUBLIC_URL: str = "https://face-recognation.tulangbawangkab.go.id"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
