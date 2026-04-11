from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os


class Settings(BaseSettings):
    # ===== API =====
    API_TITLE: str = "CODUKU Judge Service"
    API_VERSION: str = "2.0.0"
    API_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8002
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ===== JWT =====
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 720

    # ===== PostgreSQL =====
    POSTGRES_URL: str = os.getenv(
        "POSTGRES_URL",
        "postgresql://postgres:postgres@postgres:5432/coduku"
    )
    POSTGRES_POOL_SIZE: int = int(os.getenv("POSTGRES_POOL_SIZE", "20"))
    POSTGRES_POOL_TIMEOUT: int = int(os.getenv("POSTGRES_POOL_TIMEOUT", "30"))
    POSTGRES_MAX_CACHED_STATEMENT_LIFETIME: int = 3600
    POSTGRES_MAX_CACHEABLE_STATEMENT_SIZE: int = 15000

    # ===== Supabase =====
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL", None)
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY", None)
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY", None)

    # ===== Redis =====
    UPSTASH_REDIS_URL: str = os.getenv("UPSTASH_REDIS_URL", "redis://redis:6379/2")
    REDIS_NAMESPACE: str = "coduku"
    REDIS_TTL: int = 86400  # 24 hours

    # ===== Judge0 =====
    JUDGE0_URL: str = os.getenv("JUDGE0_URL", "http://judge0:2358")
    JUDGE0_TIMEOUT: int = int(os.getenv("JUDGE0_TIMEOUT", "60"))
    JUDGE0_API_KEY: str = os.getenv("JUDGE0_API_KEY", "")
    JUDGE0_MAX_RETRIES: int = 3
    JUDGE0_CIRCUIT_BREAKER_THRESHOLD: int = 5
    JUDGE0_CIRCUIT_BREAKER_TIMEOUT: int = 60
    JUDGE0_INITIAL_POLL_DELAY: float = 0.5
    JUDGE0_MAX_POLL_DELAY: float = 2.0
    JUDGE0_MAX_POLLS: int = 60

    # ===== Code Execution Limits =====
    MAX_SUBMISSION_SIZE: int = int(os.getenv("MAX_SUBMISSION_SIZE", "4096"))
    TIME_LIMIT_SECONDS: int = int(os.getenv("TIME_LIMIT_SECONDS", "10"))
    MEMORY_LIMIT_MB: int = int(os.getenv("MEMORY_LIMIT_MB", "262144"))
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", "1000"))

    # ===== Rate Limiting =====
    MAX_SUBMISSIONS_PER_HOUR: int = 100
    MAX_CONCURRENT_SUBMISSIONS: int = 50

    # ===== Logging =====
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # ===== Leaderboard Service =====
    LEADERBOARD_URL: str = os.getenv("LEADERBOARD_URL", "http://leaderboard:8003")
    LEADERBOARD_TIMEOUT: int = 10

    # ===== Output Normalization =====
    OUTPUT_NORMALIZE_MODE: str = os.getenv("OUTPUT_NORMALIZE_MODE", "lines")
    ENABLE_FUZZY_MATCHING: bool = os.getenv("ENABLE_FUZZY_MATCHING", "false").lower() == "true"
    FLOAT_TOLERANCE: float = 1e-6

    # ===== Error Handling =====
    ENABLE_CIRCUIT_BREAKER: bool = True
    ENABLE_RETRY_LOGIC: bool = True
    ENABLE_DETAILED_ERRORS: bool = os.getenv("ENABLE_DETAILED_ERRORS", "false").lower() == "true"

    # ===== CORS =====
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost",
        "http://localhost:80",
        "*",
    ]

    # ===== MongoDB =====
    MONGODB_URL: Optional[str] = os.getenv("MONGODB_URL", None)

    class Config:
        env_file = ".env"
        case_sensitive = True
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()