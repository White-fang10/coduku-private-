"""User Service - Handle all user-related operations"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import main

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# ====== MODELS ======
class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    house: str
    total_score: int
    problems_solved: int
    submissions: int
    created_at: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    rank: Optional[int] = None

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserStats(BaseModel):
    total_score: int
    problems_solved: int
    submissions: int
    accepted_submissions: int = 0
    wrong_answer: int = 0
    runtime_errors: int = 0
    time_limit_exceeded: int = 0
    average_execution_time: float = 0
    languages_used: list[str] = []

# ====== ENDPOINTS ======
@router.get("/me", response_model=UserProfile)
async def get_current_user(payload: dict = Depends(main.verify_jwt_token)):
    """Get current user profile"""
    email = payload.get("email")
    user = await main.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get user rank
    users_list = await main.get_leaderboard_users_sorted()
    rank = None
    for idx, u in enumerate(users_list):
        if u.get("email") == email:
            rank = idx + 1
            break
    
    return UserProfile(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        house=user.get("house", "gryffindor"),
        total_score=user.get("total_score", 0),
        problems_solved=user.get("problems_solved", 0),
        submissions=user.get("submissions", 0),
        created_at=user.get("created_at", datetime.utcnow().isoformat()),
        rank=rank
    )


@router.get("/{user_id}", response_model=UserProfile)
async def get_user(user_id: str, payload: dict = Depends(main.verify_jwt_token)):
    """Get user profile by ID"""
    # Search for user by ID in the users_db
    for email, user in main.users_db.items():
        if user.get("id") == user_id:
            # Get user rank
            users_list = await main.get_leaderboard_users_sorted()
            rank = None
            for idx, u in enumerate(users_list):
                if u.get("id") == user_id:
                    rank = idx + 1
                    break
            
            return UserProfile(
                id=user["id"],
                name=user["name"],
                email=user["email"],
                house=user.get("house", "gryffindor"),
                total_score=user.get("total_score", 0),
                problems_solved=user.get("problems_solved", 0),
                submissions=user.get("submissions", 0),
                created_at=user.get("created_at", datetime.utcnow().isoformat()),
                rank=rank
            )
    
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/email/{email}", response_model=UserProfile)
async def get_user_by_email(email: str, payload: dict = Depends(main.verify_jwt_token)):
    """Get user profile by email"""
    user = await main.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user rank
    users_list = await main.get_leaderboard_users_sorted()
    rank = None
    for idx, u in enumerate(users_list):
        if u.get("email") == email:
            rank = idx + 1
            break
    
    return UserProfile(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        house=user.get("house", "gryffindor"),
        total_score=user.get("total_score", 0),
        problems_solved=user.get("problems_solved", 0),
        submissions=user.get("submissions", 0),
        created_at=user.get("created_at", datetime.utcnow().isoformat()),
        rank=rank
    )


@router.patch("/me", response_model=UserProfile)
async def update_profile(request: UserUpdateRequest, payload: dict = Depends(main.verify_jwt_token)):
    """Update current user profile"""
    email = payload.get("email")
    user = await main.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Update user data
    if request.name:
        user["name"] = request.name
    if request.bio:
        user["bio"] = request.bio
    if request.avatar_url:
        user["avatar_url"] = request.avatar_url
    
    # Persist to database
    if main.mongo_enabled and main._users_coll is not None:
        await main._users_coll.update_one(
            {"email": email},
            {"$set": {
                "name": user["name"],
                "bio": user.get("bio"),
                "avatar_url": user.get("avatar_url")
            }}
        )
    
    # Get user rank
    users_list = await main.get_leaderboard_users_sorted()
    rank = None
    for idx, u in enumerate(users_list):
        if u.get("email") == email:
            rank = idx + 1
            break
    
    return UserProfile(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        house=user.get("house", "gryffindor"),
        total_score=user.get("total_score", 0),
        problems_solved=user.get("problems_solved", 0),
        submissions=user.get("submissions", 0),
        created_at=user.get("created_at", datetime.utcnow().isoformat()),
        rank=rank
    )


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(payload: dict = Depends(main.verify_jwt_token)):
    """Get detailed user statistics"""
    user_id = payload.get("sub")
    
    submissions = await main.get_submissions_for_user(user_id)
    
    accepted_count = 0
    wrong_answer = 0
    runtime_errors = 0
    tle_count = 0
    total_time = 0
    languages = set()
    
    for sub in submissions:
        if sub.get("status") == "accepted":
            accepted_count += 1
        elif sub.get("status") == "wrong_answer":
            wrong_answer += 1
        elif sub.get("status") in ["runtime_error", "compilation_error"]:
            runtime_errors += 1
        elif sub.get("status") == "time_limit_exceeded":
            tle_count += 1
        
        if sub.get("execution_time_ms"):
            total_time += sub["execution_time_ms"]
        
        if sub.get("language"):
            languages.add(sub["language"])
    
    user = await main.get_user_by_email(payload.get("email"))
    
    avg_time = total_time / len(submissions) if submissions else 0
    
    return UserStats(
        total_score=user.get("total_score", 0),
        problems_solved=user.get("problems_solved", 0),
        submissions=len(submissions),
        accepted_submissions=accepted_count,
        wrong_answer=wrong_answer,
        runtime_errors=runtime_errors,
        time_limit_exceeded=tle_count,
        average_execution_time=avg_time,
        languages_used=list(languages)
    )


@router.get("/search/{query}")
async def search_users(query: str, payload: dict = Depends(main.verify_jwt_token)):
    """Search users by name or email"""
    results = []
    query_lower = query.lower()
    
    for email, user in main.users_db.items():
        if (query_lower in user.get("name", "").lower() or
            query_lower in user.get("email", "").lower()):
            results.append({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "house": user.get("house", "gryffindor"),
                "total_score": user.get("total_score", 0)
            })
    
    return results[:20]  # Limit to 20 results
