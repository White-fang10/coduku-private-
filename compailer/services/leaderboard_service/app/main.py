"""
CODUKU Leaderboard Service
Real-time rankings with global and house-based standings
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional,  Dict, Any
import logging
from datetime import datetime
import asyncpg
import redis
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Leaderboard Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== CONFIG =====
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@postgres:5432/coduku")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/2")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8003))

# Global Redis and PostgreSQL connections
redis_client = None
postgres_pool = None

# ===== MODELS =====
class UpdateScoreRequest(BaseModel):
    user_id: str
    username: str
    house: str
    problem_id: int
    points: int
    language: str

class UserStats(BaseModel):
    user_id: str
    username: str
    house: str
    total_points: int
    problems_solved: int
    acceptance_rate: float
    global_rank: int
    house_rank: int

class HouseStats(BaseModel):
    house: str
    total_points: int
    members: int
    average_points: float
    house_rank: int

# ===== INITIALIZATION =====
@app.on_event("startup")
async def startup():
    """Initialize database and cache connections"""
    global redis_client, postgres_pool
    
    logger.info(f"Starting Leaderboard Service on port {SERVICE_PORT}")
    
    # Connect to Redis
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        redis_client = None
    
    # Connect to PostgreSQL
    try:
        postgres_pool = await asyncpg.create_pool(POSTGRES_URL, min_size=5, max_size=20)
        logger.info("✅ PostgreSQL connected")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        postgres_pool = None
    
    # Initialize database schema
    await initialize_database()

@app.on_event("shutdown")
async def shutdown():
    """Close database connections"""
    global redis_client, postgres_pool
    
    if postgres_pool:
        await postgres_pool.close()
        logger.info("PostgreSQL pool closed")

# ===== DATABASE INITIALIZATION =====
async def initialize_database():
    """Create tables if they don't exist"""
    if not postgres_pool:
        logger.error("PostgreSQL pool not available")
        return
    
    async with postgres_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard_users (
                user_id VARCHAR(100) PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                house VARCHAR(50) NOT NULL,
                total_points INT DEFAULT 0,
                problems_solved INT DEFAULT 0,
                submissions INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard_submissions (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                problem_id INT NOT NULL,
                language VARCHAR(20),
                verdict VARCHAR(30),
                points INT,
                submitted_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS house_stats (
                house VARCHAR(50) PRIMARY KEY,
                total_points INT DEFAULT 0,
                members INT DEFAULT 0,
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_lb_submissions_user_id ON leaderboard_submissions(user_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_lb_users_house ON leaderboard_users(house)
        """)
        
        logger.info("Database schema initialized")

# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_ok = False
    postgres_ok = False
    
    if redis_client:
        try:
            redis_client.ping()
            redis_ok = True
        except:
            pass
    
    if postgres_pool:
        try:
            async with postgres_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            postgres_ok = True
        except:
            pass
    
    return {
        "status": "healthy" if (redis_ok and postgres_ok) else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
        "postgres": "connected" if postgres_ok else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }

# ===== CORE FUNCTIONALITY =====
@app.post("/api/v1/update_score")
async def update_score(request: UpdateScoreRequest):
    """Update user score and leaderboard ranking"""
    try:
        if not postgres_pool:
            raise Exception("Database not connected")
        
        async with postgres_pool.acquire() as conn:
            # Get or create user
            user = await conn.fetchrow(
                "SELECT * FROM leaderboard_users WHERE user_id = $1",
                request.user_id
            )
            
            if not user:
                # New user
                await conn.execute("""
                    INSERT INTO leaderboard_users (user_id, username, house, total_points, problems_solved, submissions)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, request.user_id, request.username, request.house, request.points, 1, 1)
            else:
                # Update existing user - add points and increment problems solved
                await conn.execute("""
                    UPDATE leaderboard_users 
                    SET total_points = total_points + $1,
                        problems_solved = problems_solved + 1,
                        submissions = submissions + 1
                    WHERE user_id = $2
                """, request.points, request.user_id)
            
            # Record submission
            await conn.execute("""
                INSERT INTO leaderboard_submissions (user_id, problem_id, language, verdict, points)
                VALUES ($1, $2, $3, $4, $5)
            """, request.user_id, request.problem_id, request.language, "Accepted", request.points)
            
            # Update house stats
            house_stats = await conn.fetchrow(
                "SELECT * FROM house_stats WHERE house = $1",
                request.house
            )
            
            if not house_stats:
                await conn.execute("""
                    INSERT INTO house_stats (house, total_points, members)
                    VALUES ($1, $2, $3)
                """, request.house, request.points, 1)
            else:
                await conn.execute("""
                    UPDATE house_stats 
                    SET total_points = total_points + $1,
                        updated_at = NOW()
                    WHERE house = $2
                """, request.points, request.house)
            
            logger.info(f"Score updated: {request.username} (+{request.points} pts)")
        
        # Invalidate cache
        if redis_client:
            try:
                redis_client.delete("leaderboard:global")
                redis_client.delete(f"leaderboard:house:{request.house}")
                logger.info("Leaderboard cache invalidated")
            except Exception as e:
                logger.warning(f"Cache invalidation failed: {e}")
        
        return {
            "status": "success",
            "message": f"Score updated for {request.username}",
            "points": request.points
        }
    
    except Exception as e:
        logger.error(f"Error updating score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== GLOBAL LEADERBOARD =====
@app.get("/api/v1/leaderboard")
async def get_global_leaderboard(limit: int = 50, offset: int = 0):
    """Get global leaderboard (all users ranked by points)"""
    try:
        # Try cache first
        cache_key = f"leaderboard:global:{offset}:{limit}"
        if redis_client:
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    logger.info("Returning cached leaderboard")
                    return json.loads(cached)
            except:
                pass
        
        if not postgres_pool:
            raise Exception("Database not connected")
        
        async with postgres_pool.acquire() as conn:
            # Get ranked users
            users = await conn.fetch("""
                SELECT 
                    user_id, username, house, total_points, problems_solved, submissions,
                    CASE 
                        WHEN submissions > 0 THEN ROUND(100.0 * problems_solved / submissions, 1)
                        ELSE 0 
                    END as acceptance_rate,
                    ROW_NUMBER() OVER (ORDER BY total_points DESC, problems_solved DESC) as global_rank
                FROM leaderboard_users
                ORDER BY total_points DESC, problems_solved DESC
                LIMIT $1 OFFSET $2
            """, limit, offset)
            
            # Convert to list of dicts
            leaderboard = []
            for user in users:
                leaderboard.append({
                    "rank": user["global_rank"],
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "house": user["house"],
                    "total_points": user["total_points"],
                    "problems_solved": user["problems_solved"],
                    "submissions": user["submissions"],
                    "acceptance_rate": float(user["acceptance_rate"])
                })
            
            # Get total count
            total = await conn.fetchval("SELECT COUNT(*) FROM leaderboard_users")
            
            response = {
                "status": "success",
                "total": total,
                "returned": len(leaderboard),
                "offset": offset,
                "limit": limit,
                "leaderboard": leaderboard
            }
            
            # Cache for 30 seconds
            if redis_client:
                try:
                    redis_client.setex(cache_key, 30, json.dumps(response))
                except:
                    pass
            
            return response
    
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== HOUSE LEADERBOARD =====
@app.get("/api/v1/leaderboard/house/{house_name}")
async def get_house_leaderboard(house_name: str, limit: int = 50, offset: int = 0):
    """Get leaderboard for a specific house"""
    try:
        cache_key = f"leaderboard:house:{house_name}:{offset}:{limit}"
        if redis_client:
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except:
                pass
        
        if not postgres_pool:
            raise Exception("Database not connected")
        
        async with postgres_pool.acquire() as conn:
            # Get house members ranked by points
            users = await conn.fetch("""
                SELECT 
                    user_id, username, house, total_points, problems_solved, submissions,
                    CASE 
                        WHEN submissions > 0 THEN ROUND(100.0 * problems_solved / submissions, 1)
                        ELSE 0 
                    END as acceptance_rate,
                    ROW_NUMBER() OVER (ORDER BY total_points DESC) as house_rank
                FROM leaderboard_users
                WHERE house = $1
                ORDER BY total_points DESC, problems_solved DESC
                LIMIT $2 OFFSET $3
            """, house_name, limit, offset)
            
            leaderboard = []
            for user in users:
                leaderboard.append({
                    "rank": user["house_rank"],
                    "username": user["username"],
                    "house": user["house"],
                    "total_points": user["total_points"],
                    "problems_solved": user["problems_solved"],
                    "acceptance_rate": float(user["acceptance_rate"])
                })
            
            # Get house stats
            house_stats = await conn.fetchrow(
                "SELECT * FROM house_stats WHERE house = $1",
                house_name
            )
            
            house_total = house_stats["total_points"] if house_stats else 0
            house_members = len(users)
            
            response = {
                "status": "success",
                "house": house_name,
                "total_house_points": house_total,
                "members": house_members,
                "leaderboard": leaderboard
            }
            
            if redis_client:
                try:
                    redis_client.setex(cache_key, 30, json.dumps(response))
                except:
                    pass
            
            return response
    
    except Exception as e:
        logger.error(f"Error fetching house leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== HOUSE STANDINGS =====
@app.get("/api/v1/house-standings")
async def get_house_standings():
    """Get overall house rankings"""
    try:
        cache_key = "leaderboard:house_standings"
        if redis_client:
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except:
                pass
        
        if not postgres_pool:
            raise Exception("Database not connected")
        
        async with postgres_pool.acquire() as conn:
            houses = await conn.fetch("""
                SELECT 
                    house,
                    total_points,
                    members,
                    ROUND(CAST(total_points AS NUMERIC) / NULLIF(members, 0), 2) as avg_points_per_member,
                    ROW_NUMBER() OVER (ORDER BY total_points DESC) as rank
                FROM house_stats
                ORDER BY total_points DESC
            """)
            
            standings = []
            for house in houses:
                standings.append({
                    "rank": house["rank"],
                    "house": house["house"],
                    "total_points": house["total_points"],
                    "members": house["members"],
                    "avg_points_per_member": float(house["avg_points_per_member"] or 0)
                })
            
            response = {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "houses": standings
            }
            
            if redis_client:
                try:
                    redis_client.setex(cache_key, 60, json.dumps(response))
                except:
                    pass
            
            return response
    
    except Exception as e:
        logger.error(f"Error fetching house standings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== USER PROFILE =====
@app.get("/api/v1/user/{user_id}")
async def get_user_profile(user_id: str):
    """Get user stats and submission history"""
    try:
        if not postgres_pool:
            raise Exception("Database not connected")
        
        async with postgres_pool.acquire() as conn:
            # Get user stats
            user = await conn.fetchrow(
                "SELECT * FROM leaderboard_users WHERE user_id = $1",
                user_id
            )
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get submissions
            submissions = await conn.fetch("""
                SELECT id, problem_id, language, verdict, points, submitted_at
                FROM leaderboard_submissions
                WHERE user_id = $1
                ORDER BY submitted_at DESC
                LIMIT 100
            """, user_id)
            
            # Get house rank
            house_rank = await conn.fetchval("""
                SELECT rank FROM (
                    SELECT user_id, ROW_NUMBER() OVER (ORDER BY total_points DESC) as rank
                    FROM leaderboard_users WHERE house = $1
                ) ranked WHERE user_id = $2
            """, user["house"], user_id)
            
            # Get global rank
            global_rank = await conn.fetchval("""
                SELECT rank FROM (
                    SELECT user_id, ROW_NUMBER() OVER (ORDER BY total_points DESC) as rank
                    FROM leaderboard_users
                ) ranked WHERE user_id = $1
            """, user_id)
            
            return {
                "status": "success",
                "user": {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "house": user["house"],
                    "total_points": user["total_points"],
                    "problems_solved": user["problems_solved"],
                    "submissions": user["submissions"],
                    "acceptance_rate": round(100.0 * user["problems_solved"] / max(user["submissions"], 1), 1),
                    "global_rank": global_rank,
                    "house_rank": house_rank
                },
                "submissions": submissions
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)

# ===== ALIAS ROUTES (frontend compatibility) =====
@app.get("/api/v1/leaderboards/global")
async def get_global_leaderboard_alias(limit: int = 50, offset: int = 0):
    return await get_global_leaderboard(limit=limit, offset=offset)

@app.get("/api/v1/leaderboards/houses")
async def get_house_standings_alias():
    return await get_house_standings()

@app.get("/api/v1/leaderboards/house/{house_name}")
async def get_house_leaderboard_alias(house_name: str, limit: int = 50, offset: int = 0):
    return await get_house_leaderboard(house_name=house_name, limit=limit, offset=offset)
