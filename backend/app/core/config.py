import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost:5432/opt2d"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    BACKEND_CORS_ORIGINS: str = os.getenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    )
    
    CACHE_TTL: int = 1  # 1 second for polling endpoints
    SNAPSHOT_CACHE_TTL: int = 5  # 5 seconds for larger snapshots
    
    class Config:
        env_file = ".env"

settings = Settings()
