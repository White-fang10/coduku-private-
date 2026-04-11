from supabase import create_client, Client
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class SupabaseService:
    """Supabase PostgreSQL Database Service (Auth microservice)."""

    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY,
            )
            logger.info("✅ Supabase (auth) connected")
        return cls._instance

    # ===== USER OPERATIONS =====

    @classmethod
    async def create_user(
        cls,
        email: str,
        username: str,
        password_hash: str,
        house: str,
    ) -> Optional[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("users")
                .insert(
                    {
                        "email": email,
                        "username": username,
                        "password_hash": password_hash,
                        "house": house.lower(),
                        "total_score": 0,
                        "problems_solved": 0,
                        "created_at": datetime.utcnow().isoformat(),
                    }
                )
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:  # pragma: no cover - network/remote failure
            logger.error(f"❌ Auth Supabase create_user error: {e}")
            return None

    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("users")
                .select("*")
                .eq("email", email)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Auth Supabase get_user_by_email error: {e}")
            return None

    @classmethod
    async def get_user_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        client = cls.get_client()
        try:
            response = (
                client.table("users")
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:  # pragma: no cover
            logger.error(f"❌ Auth Supabase get_user_by_id error: {e}")
            return None


supabase_service = SupabaseService()

