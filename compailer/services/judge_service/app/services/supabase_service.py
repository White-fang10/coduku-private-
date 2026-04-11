from supabase import create_client, Client
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class SupabaseService:
    """Supabase service used by judge microservice (problems + submissions)."""

    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY,
            )
            logger.info("✅ Supabase (judge) connected")
        return cls._instance

    # ===== PROBLEMS =====

    @classmethod
    async def get_problems(cls, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("problems")
                .select("*")
                .order("difficulty")
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data or []
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Judge Supabase get_problems error: {e}")
            return []

    @classmethod
    async def get_problem(cls, problem_id: int) -> Optional[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("problems")
                .select("*")
                .eq("id", problem_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Judge Supabase get_problem error: {e}")
            return None

    @classmethod
    async def get_test_cases(cls, problem_id: int) -> List[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("test_cases")
                .select("*")
                .eq("problem_id", problem_id)
                .execute()
            )
            return response.data or []
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Judge Supabase get_test_cases error: {e}")
            return []

    # ===== SUBMISSIONS =====

    @classmethod
    async def create_submission(
        cls,
        user_id: str,
        problem_id: int,
        language: str,
        source_code: str,
    ) -> Optional[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("submissions")
                .insert(
                    {
                        "user_id": user_id,
                        "problem_id": problem_id,
                        "language": language,
                        "source_code": source_code,
                        "status": "pending",
                        "test_cases_passed": 0,
                        "test_cases_total": 0,
                        "score": 0,
                        "created_at": datetime.utcnow().isoformat(),
                    }
                )
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Judge Supabase create_submission error: {e}")
            return None

    @classmethod
    async def update_submission(cls, submission_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        client = cls.get_client()
        try:
            kwargs["updated_at"] = datetime.utcnow().isoformat()
            response = (
                client.table("submissions")
                .update(kwargs)
                .eq("id", submission_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Judge Supabase update_submission error: {e}")
            return None

    @classmethod
    async def get_submission(cls, submission_id: str) -> Optional[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("submissions")
                .select("*")
                .eq("id", submission_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Judge Supabase get_submission error: {e}")
            return None

    @classmethod
    async def get_user_submissions(cls, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("submissions")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Judge Supabase get_user_submissions error: {e}")
            return []


supabase_service = SupabaseService()

