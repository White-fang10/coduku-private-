import json
import logging
from typing import Any, List, Optional, Tuple

import redis
from redis import Redis

from app.core.config import settings


logger = logging.getLogger(__name__)


class RedisService:
    """Redis client dedicated to leaderboard lookups."""

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
                logger.info("✅ Redis (leaderboard) connected")
            except Exception as e:  # pragma: no cover
                logger.error(f"❌ Redis (leaderboard) connection failed: {e}")
                raise
        return cls._instance

    @classmethod
    async def get_leaderboard(
        cls, leaderboard: str, start: int = 0, stop: int = 99
    ) -> List[Tuple[str, int]]:
        try:
            client = cls.get_client()
            key = f"{settings.REDIS_NAMESPACE}:leaderboard:{leaderboard}"
            rows = client.zrevrange(key, start, stop, withscores=True)
            return [(user, int(float(score))) for user, score in rows]
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Redis (leaderboard) get_leaderboard error: {e}")
            return []


redis_service = RedisService()

