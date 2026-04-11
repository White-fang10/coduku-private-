"""PostgreSQL Service for Auth Microservice"""

import asyncpg
import logging
import os
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class PostgreSQLService:
    """PostgreSQL connection pool and query service"""
    
    _pool = None
    
    @classmethod
    async def init_pool(cls):
        """Initialize connection pool"""
        if cls._pool is None:
            try:
                # Use environment variable or default
                # In docker, 'postgres' is the hostname.
                db_url = os.getenv("POSTGRES_URL") or "postgresql://postgres:postgres@postgres:5432/coduku"
                cls._pool = await asyncpg.create_pool(
                    db_url,
                    min_size=2,
                    max_size=10,
                )
                logger.info("✅ Auth PostgreSQL pool initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Auth PostgreSQL pool: {e}")
                # Don't raise, allowing in-memory fallback if needed
    
    @classmethod
    async def create_user(
        cls,
        user_id: str,
        email: str,
        username: str,
        password_hash: str,
        house: str
    ) -> bool:
        """Create a new user in the database"""
        if cls._pool is None:
            await cls.init_pool()
            
        if cls._pool is None:
            logger.error("❌ PostgreSQL pool not initialized in Auth Service")
            return False
            
        try:
            async with cls._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO users (id, email, username, password_hash, house)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (email) DO NOTHING
                    """,
                    user_id, email, username, password_hash, house.lower()
                )
                
                # Also initialize leaderboard entry
                await conn.execute(
                    """
                    INSERT INTO leaderboard (user_id, total_score, problems_solved)
                    VALUES ($1, 0, 0)
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    user_id
                )
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create user in database: {e}")
            return False

    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if cls._pool is None:
            await cls.init_pool()
            
        if cls._pool is None:
            return None
            
        try:
            async with cls._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM users WHERE email = $1",
                    email
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get user by email {email}: {e}")
            return None
