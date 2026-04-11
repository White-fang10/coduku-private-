"""PostgreSQL Service for Judge Microservice"""

import asyncpg
import logging
from typing import List, Dict, Any, Optional
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
                # Parse DATABASE_URL or use default
                db_url = settings.POSTGRES_URL or "postgresql://postgres:postgres@postgres:5432/coduku"
                cls._pool = await asyncpg.create_pool(
                    db_url,
                    min_size=5,
                    max_size=20,
                    command_timeout=10,
                )
                logger.info("✅ PostgreSQL pool initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize PostgreSQL pool: {e}")
                raise
    
    @classmethod
    async def get_problems(cls, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all problems"""
        try:
            async with cls._pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT id, title, description, difficulty, score, time_limit, memory_limit FROM problems ORDER BY difficulty, id LIMIT $1 OFFSET $2",
                    limit,
                    offset
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get problems: {e}")
            return []
    
    @classmethod
    async def get_problem(cls, problem_id: int) -> Optional[Dict[str, Any]]:
        """Get single problem by ID"""
        try:
            async with cls._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT id, title, description, difficulty, score, time_limit, memory_limit FROM problems WHERE id = $1",
                    problem_id
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get problem {problem_id}: {e}")
            return None
    
    @classmethod
    async def get_test_cases(cls, problem_id: int) -> List[Dict[str, Any]]:
        """Get test cases for a problem"""
        try:
            async with cls._pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT id, problem_id, input, output, visible FROM test_cases WHERE problem_id = $1 ORDER BY id",
                    problem_id
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get test cases for problem {problem_id}: {e}")
            return []
    
    @classmethod
    async def create_submission(
        cls,
        user_id: str,
        problem_id: int,
        language: str,
        source_code: str,
    ) -> Optional[Dict[str, Any]]:
        """Create a new submission"""
        try:
            if cls._pool is None:
                logger.error("❌ PostgreSQL pool not initialized")
                return None
            
            async with cls._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO submissions (user_id, problem_id, language, source_code, status)
                    VALUES ($1, $2, $3, $4, 'pending')
                    RETURNING id, user_id, problem_id, language, source_code, status, created_at
                    """,
                    user_id, problem_id, language, source_code
                )
                if row:
                    logger.info(f"✅ Created submission {row['id']} for user {user_id}, problem {problem_id}")
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to create submission for user {user_id}, problem {problem_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @classmethod
    async def update_submission(
        cls,
        submission_id: str,
        status: str,
        test_cases_passed: int,
        test_cases_total: int,
        score: int,
    ) -> bool:
        """Update submission with results"""
        try:
            async with cls._pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE submissions 
                    SET status = $1, test_cases_passed = $2, test_cases_total = $3, score = $4, updated_at = NOW()
                    WHERE id = $5
                    """,
                    status, test_cases_passed, test_cases_total, score, submission_id
                )
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update submission {submission_id}: {e}")
            return False
    
    @classmethod
    async def get_submission(cls, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission details"""
        try:
            async with cls._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM submissions WHERE id = $1",
                    submission_id
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get submission {submission_id}: {e}")
            return None
    
    @classmethod
    async def update_leaderboard(cls, user_id: str, problem_id: int, score: int, is_accepted: bool, submission_id: str = None) -> bool:
        """Update leaderboard after submission"""
        try:
            async with cls._pool.acquire() as conn:
                if not is_accepted:
                    return False
                
                # Count accepted submissions for this problem (excluding current one if provided)
                if submission_id:
                    count = await conn.fetchval(
                        "SELECT COUNT(*) FROM submissions WHERE user_id = $1 AND problem_id = $2 AND status = 'accepted' AND id != $3",
                        user_id, problem_id, submission_id
                    )
                else:
                    count = await conn.fetchval(
                        "SELECT COUNT(*) FROM submissions WHERE user_id = $1 AND problem_id = $2 AND status = 'accepted'",
                        user_id, problem_id
                    )
                
                # Only update if this is the FIRST accepted submission for this problem
                if count == 0:
                    await conn.execute(
                        """
                        UPDATE leaderboard
                        SET total_score = total_score + $1,
                            problems_solved = problems_solved + 1,
                            last_submission = NOW(),
                            updated_at = NOW()
                        WHERE user_id = $2
                        """,
                        score, user_id
                    )
                    logger.info(f"✅ Updated leaderboard for user {user_id}: +{score} points, +1 problem")
                    return True
                else:
                    logger.debug(f"⚠️  Skipped leaderboard update for user {user_id}, problem {problem_id} (user already solved this problem)")
                    return False
        except Exception as e:
            logger.error(f"❌ Failed to update leaderboard for user {user_id}: {e}")
            return False
