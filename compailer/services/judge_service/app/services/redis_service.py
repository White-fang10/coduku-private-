import json
import logging
from typing import Any, Optional, Tuple, List

import redis
from redis import Redis

from app.core.config import settings


logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for judge (leaderboards + misc caching)."""

    _instance: Optional[Redis] = None

    @classmethod
    def get_client(cls) -> Redis:
        if cls._instance is None:
            try:
                cls._instance = redis.from_url(
                    settings.UPSTASH_REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                )
                cls._instance.ping()
                logger.info("✅ Redis (judge) connected")
            except Exception as e:  # pragma: no cover
                logger.error(f"❌ Redis (judge) connection failed: {e}")
                raise
        return cls._instance

    @classmethod
    async def add_to_leaderboard(cls, leaderboard: str, user_id: str, score: float) -> None:
        try:
            client = cls.get_client()
            key = f"{settings.REDIS_NAMESPACE}:leaderboard:{leaderboard}"
            client.zadd(key, {user_id: score})
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Redis (judge) add_to_leaderboard error: {e}")


redis_service = RedisService()

