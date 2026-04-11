"""Admin Service - Handle admin-only operations"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import main
import uuid
import json

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# ====== MODELS ======
class TestCaseRequest(BaseModel):
    input: str
    output: str
    visible: bool = True

class ProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str  # easy, medium, hard
    base_score: int = 100
    difficulty_multiplier: float = 1.0
    time_limit: float = 5.0
    memory_limit: int = 256
    test_cases: List[TestCaseRequest]

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    base_score: Optional[int] = None
    difficulty_multiplier: Optional[float] = None
    time_limit: Optional[float] = None
    memory_limit: Optional[int] = None

class ProblemResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    score: int
    time_limit: float
    memory_limit: int
    test_cases_count: int

# ====== ADMIN VERIFICATION ======
async def verify_admin(payload: dict = Depends(main.verify_jwt_token)) -> dict:
    """Verify user is admin"""
    email = payload.get("email")
    user = await main.get_user_by_email(email)
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

# ====== PROBLEM MANAGEMENT ENDPOINTS ======

@router.post("/problems", response_model=ProblemResponse)
async def create_problem(request: ProblemCreate, payload: dict = Depends(verify_admin)):
    """Create a new problem (admin only)"""
    
    # Generate problem ID
    pid_num = len(main.problems_db) + 1
    while f"p{pid_num}" in main.problems_db:
        pid_num += 1
    pid = f"p{pid_num}"
    
    # Calculate score from base score and difficulty multiplier
    score = int(request.base_score * request.difficulty_multiplier)
    
    new_problem = {
        "id": pid,
        "title": request.title,
        "description": request.description,
        "difficulty": request.difficulty.lower(),
        "score": score,
        "base_score": request.base_score,
        "difficulty_multiplier": request.difficulty_multiplier,
        "time_limit": request.time_limit,
        "memory_limit": request.memory_limit,
        "test_cases": [
            {
                "input": tc.input,
                "output": tc.output,
                "visible": tc.visible
            }
            for tc in request.test_cases
        ],
        "created_at": datetime.utcnow().isoformat(),
        "created_by": payload.get("email")
    }
    
    main.problems_db[pid] = new_problem
    
    # Persist to MongoDB if enabled
    if main.mongo_enabled and main._mongo_db is not None:
        try:
            problems_coll = main._mongo_db["problems"]
            await problems_coll.insert_one(new_problem)
        except Exception as e:
            print(f"MongoDB insert problem failed: {e}")
    
    return ProblemResponse(
        id=new_problem["id"],
        title=new_problem["title"],
        description=new_problem["description"],
        difficulty=new_problem["difficulty"],
        score=new_problem["score"],
        time_limit=new_problem["time_limit"],
        memory_limit=new_problem["memory_limit"],
        test_cases_count=len(new_problem["test_cases"])
    )


@router.get("/problems", response_model=List[ProblemResponse])
async def list_problems(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    payload: dict = Depends(verify_admin)
):
    """List all problems (admin only)"""
    problems_list = list(main.problems_db.values())
    problems_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    paginated = problems_list[skip:skip + limit]
    
    return [
        ProblemResponse(
            id=p["id"],
            title=p["title"],
            description=p["description"],
            difficulty=p["difficulty"],
            score=p["score"],
            time_limit=p["time_limit"],
            memory_limit=p["memory_limit"],
            test_cases_count=len(p.get("test_cases", []))
        )
        for p in paginated
    ]


@router.get("/problems/{problem_id}", response_model=dict)
async def get_problem(problem_id: str, payload: dict = Depends(verify_admin)):
    """Get problem details (admin only - includes all test cases)"""
    if problem_id not in main.problems_db:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    return main.problems_db[problem_id]


@router.patch("/problems/{problem_id}", response_model=ProblemResponse)
async def update_problem(problem_id: str, request: ProblemUpdate, payload: dict = Depends(verify_admin)):
    """Update problem (admin only)"""
    if problem_id not in main.problems_db:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    problem = main.problems_db[problem_id]
    
    # Update fields
    if request.title:
        problem["title"] = request.title
    if request.description:
        problem["description"] = request.description
    if request.difficulty:
        problem["difficulty"] = request.difficulty.lower()
    if request.base_score:
        problem["base_score"] = request.base_score
    if request.difficulty_multiplier:
        problem["difficulty_multiplier"] = request.difficulty_multiplier
    if request.time_limit:
        problem["time_limit"] = request.time_limit
    if request.memory_limit:
        problem["memory_limit"] = request.memory_limit
    
    # Recalculate score
    if request.base_score or request.difficulty_multiplier:
        base_score = problem.get("base_score", 100)
        multiplier = problem.get("difficulty_multiplier", 1.0)
        problem["score"] = int(base_score * multiplier)
    
    problem["updated_at"] = datetime.utcnow().isoformat()
    problem["updated_by"] = payload.get("email")
    
    # Persist to MongoDB if enabled
    if main.mongo_enabled and main._mongo_db is not None:
        try:
            problems_coll = main._mongo_db["problems"]
            await problems_coll.update_one(
                {"id": problem_id},
                {"$set": problem}
            )
        except Exception as e:
            print(f"MongoDB update problem failed: {e}")
    
    return ProblemResponse(
        id=problem["id"],
        title=problem["title"],
        description=problem["description"],
        difficulty=problem["difficulty"],
        score=problem["score"],
        time_limit=problem["time_limit"],
        memory_limit=problem["memory_limit"],
        test_cases_count=len(problem.get("test_cases", []))
    )


@router.delete("/problems/{problem_id}")
async def delete_problem(problem_id: str, payload: dict = Depends(verify_admin)):
    """Delete problem (admin only)"""
    if problem_id not in main.problems_db:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    del main.problems_db[problem_id]
    
    # Delete from MongoDB if enabled
    if main.mongo_enabled and main._mongo_db is not None:
        try:
            problems_coll = main._mongo_db["problems"]
            await problems_coll.delete_one({"id": problem_id})
        except Exception as e:
            print(f"MongoDB delete problem failed: {e}")
    
    return {"message": "Problem deleted successfully"}


@router.post("/problems/{problem_id}/test-cases")
async def add_test_cases(
    problem_id: str,
    test_cases: List[TestCaseRequest],
    payload: dict = Depends(verify_admin)
):
    """Add test cases to problem"""
    if problem_id not in main.problems_db:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    problem = main.problems_db[problem_id]
    
    for tc in test_cases:
        problem["test_cases"].append({
            "input": tc.input,
            "output": tc.output,
            "visible": tc.visible
        })
    
    # Persist to MongoDB if enabled
    if main.mongo_enabled and main._mongo_db is not None:
        try:
            problems_coll = main._mongo_db["problems"]
            await problems_coll.update_one(
                {"id": problem_id},
                {"$set": {"test_cases": problem["test_cases"]}}
            )
        except Exception as e:
            print(f"MongoDB update test cases failed: {e}")
    
    return {
        "message": f"Added {len(test_cases)} test cases",
        "total_test_cases": len(problem["test_cases"])
    }


# ====== USER MANAGEMENT ENDPOINTS ======

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    house: Optional[str] = None,
    payload: dict = Depends(verify_admin)
):
    """List all users (admin only)"""
    users_list = list(main.users_db.values())
    
    # Filter by house if specified
    if house:
        users_list = [u for u in users_list if u.get("house", "").lower() == house.lower()]
    
    # Sort by score descending
    users_list.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    
    paginated = users_list[skip:skip + limit]
    
    return [
        {
            "id": u["id"],
            "name": u["name"],
            "email": u["email"],
            "house": u.get("house", "gryffindor"),
            "total_score": u.get("total_score", 0),
            "problems_solved": u.get("problems_solved", 0),
            "submissions": u.get("submissions", 0),
            "created_at": u.get("created_at", "")
        }
        for u in paginated
    ]


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str,
    payload: dict = Depends(verify_admin)
):
    """Update user role"""
    valid_roles = ["student", "mentor", "admin"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {valid_roles}")
    
    # Find user by ID
    target_user = None
    target_email = None
    for email, user in main.users_db.items():
        if user.get("id") == user_id:
            target_user = user
            target_email = email
            break
    
    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    target_user["role"] = role
    
    # Persist to MongoDB if enabled
    if main.mongo_enabled and main._users_coll is not None:
        await main._users_coll.update_one(
            {"id": user_id},
            {"$set": {"role": role}}
        )
    
    return {"message": f"User role updated to {role}"}


# ====== ANALYTICS & REPORTS ======

@router.get("/analytics/overview")
async def get_analytics_overview(payload: dict = Depends(verify_admin)):
    """Get system analytics overview"""
    total_users = len(main.users_db)
    total_problems = len(main.problems_db)
    total_submissions = len(main.submissions_db)
    
    # Calculate house stats
    house_stats = {}
    for house in ["gryffindor", "hufflepuff", "ravenclaw", "slytherin"]:
        members = [u for u in main.users_db.values() if u.get("house", "").lower() == house.lower()]
        total_score = sum(u.get("total_score", 0) for u in members)
        house_stats[house] = {
            "members": len(members),
            "total_score": total_score,
            "avg_score": total_score / len(members) if members else 0
        }
    
    # Get recent submissions
    recent_submissions = sorted(
        main.submissions_db.values(),
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )[:10]
    
    return {
        "total_users": total_users,
        "total_problems": total_problems,
        "total_submissions": total_submissions,
        "house_stats": house_stats,
        "recent_submissions": recent_submissions
    }


@router.get("/analytics/problems")
async def get_problem_analytics(payload: dict = Depends(verify_admin)):
    """Get problem analytics"""
    analytics = []
    
    for problem_id, problem in main.problems_db.items():
        submissions_for_problem = [
            s for s in main.submissions_db.values()
            if s.get("problem_id") == problem_id
        ]
        
        accepted = sum(1 for s in submissions_for_problem if s.get("status") == "accepted")
        
        analytics.append({
            "id": problem_id,
            "title": problem["title"],
            "difficulty": problem["difficulty"],
            "total_submissions": len(submissions_for_problem),
            "accepted": accepted,
            "acceptance_rate": accepted / len(submissions_for_problem) * 100 if submissions_for_problem else 0
        })
    
    return sorted(analytics, key=lambda x: x["total_submissions"], reverse=True)


# ====== HEALTH & STATUS ======

@router.get("/health")
async def admin_health(payload: dict = Depends(verify_admin)):
    """Get system health status"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "mongo_enabled": main.mongo_enabled,
        "redis_enabled": main.redis_enabled,
        "supabase_enabled": main.supabase_enabled,
        "judge0_api_url": main.JUDGE0_API_URL,
        "judge0_mode": main.JUDGE0_MODE
    }
