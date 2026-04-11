"""
Database persistence service for storing submissions and results
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import asyncpg
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Handle all database operations for Judge Service"""
    
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def initialize(cls):
        """Initialize database connection pool"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(
                    dsn=settings.POSTGRES_URL,
                    min_size=5,
                    max_size=20,
                    command_timeout=30,
                    max_cached_statement_lifetime=3600,
                    max_cacheable_statement_size=15000,
                )
                logger.info("✅ Database pool initialized")
                await cls._setup_tables()
            except Exception as e:
                logger.error(f"❌ Database initialization failed: {e}")
                raise
    
    @classmethod
    async def close(cls):
        """Close database connection pool"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("Database pool closed")
    
    @classmethod
    async def _setup_tables(cls):
        """Create database tables if they don't exist"""
        async with cls._pool.acquire() as conn:
            try:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS submissions (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        problem_id INTEGER NOT NULL,
                        language VARCHAR(50) NOT NULL,
                        source_code TEXT NOT NULL,
                        verdict VARCHAR(50) DEFAULT 'Pending',
                        score INTEGER DEFAULT 0,
                        passed_tests INTEGER DEFAULT 0,
                        total_tests INTEGER DEFAULT 0,
                        execution_time FLOAT DEFAULT 0.0,
                        compile_error TEXT,
                        runtime_error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sub_user_id ON submissions(user_id)
                """)
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sub_problem_id ON submissions(problem_id)
                """)
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sub_verdict ON submissions(verdict)
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS test_results (
                        id SERIAL PRIMARY KEY,
                        submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
                        test_case_id INTEGER NOT NULL,
                        verdict VARCHAR(50) NOT NULL,
                        actual_output TEXT,
                        error_message TEXT,
                        execution_time FLOAT DEFAULT 0.0,
                        stderr TEXT,
                        compile_output TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tr_submission_id ON test_results(submission_id)
                """)
                logger.info("✅ Database tables initialized")
            except Exception as e:
                logger.warning(f"⚠️ Table creation issue (may already exist): {e}")
    
    @classmethod
    async def save_submission(
        cls,
        user_id: str,
        problem_id: int,
        language: str,
        source_code: str,
        verdict: str,
        score: int,
        passed_tests: int,
        total_tests: int,
        execution_time: float,
        compile_error: Optional[str] = None,
        runtime_error: Optional[str] = None
    ) -> int:
        """Save submission to database"""
        query = """
            INSERT INTO submissions (
                user_id, problem_id, language, source_code, 
                verdict, score, passed_tests, total_tests, 
                execution_time, compile_error, runtime_error
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING id
        """
        
        async with cls._pool.acquire() as conn:
            try:
                submission_id = await conn.fetchval(
                    query,
                    user_id, problem_id, language, source_code,
                    verdict, score, passed_tests, total_tests,
                    execution_time, compile_error, runtime_error
                )
                logger.debug(f"✅ Submission saved: ID={submission_id}")
                return submission_id
            except Exception as e:
                logger.error(f"❌ Failed to save submission: {e}")
                raise
    
    @classmethod
    async def save_test_result(
        cls,
        submission_id: int,
        test_case_id: int,
        verdict: str,
        actual_output: Optional[str] = None,
        error_message: Optional[str] = None,
        execution_time: float = 0.0,
        stderr: Optional[str] = None,
        compile_output: Optional[str] = None
    ) -> int:
        """Save individual test case result"""
        query = """
            INSERT INTO test_results (
                submission_id, test_case_id, verdict, actual_output,
                error_message, execution_time, stderr, compile_output
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        
        async with cls._pool.acquire() as conn:
            try:
                result_id = await conn.fetchval(
                    query,
                    submission_id, test_case_id, verdict, actual_output,
                    error_message, execution_time, stderr, compile_output
                )
                return result_id
            except Exception as e:
                logger.error(f"❌ Failed to save test result: {e}")
                raise
    
    @classmethod
    async def get_submission(cls, submission_id: int) -> Optional[Dict]:
        """Retrieve submission details"""
        query = "SELECT * FROM submissions WHERE id = $1"
        
        async with cls._pool.acquire() as conn:
            row = await conn.fetchrow(query, submission_id)
            return dict(row) if row else None
    
    @classmethod
    async def get_submission_results(cls, submission_id: int) -> List[Dict]:
        """Get all test case results for a submission"""
        query = "SELECT * FROM test_results WHERE submission_id = $1 ORDER BY test_case_id"
        
        async with cls._pool.acquire() as conn:
            rows = await conn.fetch(query, submission_id)
            return [dict(row) for row in rows]
    
    @classmethod
    async def get_user_submissions(
        cls,
        user_id: str,
        problem_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get user submissions history"""
        if problem_id:
            query = """
                SELECT * FROM submissions 
                WHERE user_id = $1 AND problem_id = $2
                ORDER BY created_at DESC
                LIMIT $3
            """
            args = (user_id, problem_id, limit)
        else:
            query = """
                SELECT * FROM submissions 
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """
            args = (user_id, limit)
        
        async with cls._pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    @classmethod
    async def update_submission_verdict(
        cls,
        submission_id: int,
        verdict: str,
        score: int,
        passed_tests: int,
        total_tests: int,
        execution_time: float
    ) -> bool:
        """Update submission with final verdict"""
        query = """
            UPDATE submissions SET 
                verdict = $1, 
                score = $2,
                passed_tests = $3,
                total_tests = $4,
                execution_time = $5,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $6
        """
        
        async with cls._pool.acquire() as conn:
            try:
                result = await conn.execute(
                    query,
                    verdict, score, passed_tests, total_tests, execution_time, submission_id
                )
                return True
            except Exception as e:
                logger.error(f"❌ Failed to update submission: {e}")
                return False
    
    @classmethod
    async def get_statistics(cls, user_id: str) -> Dict:
        """Get submission statistics for a user"""
        query = """
            SELECT 
                COUNT(*) as total_submissions,
                SUM(CASE WHEN verdict = 'Accepted' THEN 1 ELSE 0 END) as accepted,
                SUM(CASE WHEN verdict = 'Wrong Answer' THEN 1 ELSE 0 END) as wrong_answer,
                SUM(CASE WHEN verdict = 'Runtime Error' THEN 1 ELSE 0 END) as runtime_error,
                SUM(CASE WHEN verdict = 'Compilation Error' THEN 1 ELSE 0 END) as compilation_error,
                SUM(CASE WHEN verdict = 'Time Limit Exceeded' THEN 1 ELSE 0 END) as timeout,
                AVG(execution_time) as avg_execution_time,
                MAX(execution_time) as max_execution_time
            FROM submissions
            WHERE user_id = $1
        """
        
        async with cls._pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
            return dict(row) if row else {}


# Create singleton instance
db_service = DatabaseService()
