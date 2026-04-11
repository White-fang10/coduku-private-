"""House Service - Handle house system"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import random
import main

router = APIRouter(prefix="/api/v1/houses", tags=["houses"])

# ====== MODELS ======
class HouseInfo(BaseModel):
    name: str
    emoji: str
    description: str
    color: str
    member_count: int
    total_score: int
    average_score: float
    rank: int

class HouseStats(BaseModel):
    houses: dict

# ====== HOUSE DEFINITIONS ======
HOUSES = {
    "gryffindor": {
        "emoji": "🦁",
        "description": "Brave & Bold - Values courage and chivalry",
        "color": "#DC143C",
        "color_light": "#FFB6C1"
    },
    "hufflepuff": {
        "emoji": "🦡",
        "description": "Loyal & Kind - Values fairness and hard work",
        "color": "#FFD700",
        "color_light": "#FFFACD"
    },
    "ravenclaw": {
        "emoji": "🦅",
        "description": "Wise & Creative - Values intelligence and wit",
        "color": "#4169E1",
        "color_light": "#B0C4DE"
    },
    "slytherin": {
        "emoji": "🐍",
        "description": "Cunning & Ambitious - Values ambition and cunning",
        "color": "#228B22",
        "color_light": "#90EE90"
    }
}

# ====== HELPER FUNCTIONS ======
def assign_random_house() -> str:
    """Assign a random house to a user"""
    return random.choice(list(HOUSES.keys()))

def get_house_color(house: str) -> str:
    """Get house color"""
    return HOUSES.get(house.lower(), {}).get("color", "#000000")

def get_house_emoji(house: str) -> str:
    """Get house emoji"""
    return HOUSES.get(house.lower(), {}).get("emoji", "🏰")

async def get_house_stats(house_name: str) -> dict:
    """Get statistics for a house"""
    house = house_name.lower()
    if house not in HOUSES:
        raise HTTPException(status_code=400, detail="Invalid house")
    
    members = [u for u in main.users_db.values() if u.get("house", "").lower() == house]
    total_score = sum(u.get("total_score", 0) for u in members)
    avg_score = total_score / len(members) if members else 0
    
    return {
        "name": house,
        "emoji": HOUSES[house]["emoji"],
        "description": HOUSES[house]["description"],
        "color": HOUSES[house]["color"],
        "member_count": len(members),
        "total_score": total_score,
        "average_score": round(avg_score, 2)
    }

# ====== ENDPOINTS ======

@router.get("/", response_model=dict)
async def get_all_houses(payload: dict = Depends(main.verify_jwt_token)):
    """Get all houses with their stats"""
    houses_data = {}
    
    # Get stats for all houses
    for house_name in HOUSES.keys():
        stats = await get_house_stats(house_name)
        houses_data[house_name] = stats
    
    # Get rankings
    ranked_houses = sorted(
        houses_data.items(),
        key=lambda x: x[1]["total_score"],
        reverse=True
    )
    
    for rank, (house_name, stats) in enumerate(ranked_houses):
        stats["rank"] = rank + 1
    
    return houses_data


@router.get("/{house_name}", response_model=HouseInfo)
async def get_house(house_name: str, payload: dict = Depends(main.verify_jwt_token)):
    """Get house information"""
    house = house_name.lower()
    if house not in HOUSES:
        raise HTTPException(status_code=400, detail="Invalid house")
    
    stats = await get_house_stats(house)
    
    # Get rank
    all_houses_stats = {}
    for h in HOUSES.keys():
        all_houses_stats[h] = await get_house_stats(h)
    
    ranked = sorted(
        all_houses_stats.items(),
        key=lambda x: x[1]["total_score"],
        reverse=True
    )
    
    rank = next((i + 1 for i, (h, _) in enumerate(ranked) if h == house), None)
    
    return HouseInfo(
        name=stats["name"],
        emoji=stats["emoji"],
        description=stats["description"],
        color=stats["color"],
        member_count=stats["member_count"],
        total_score=stats["total_score"],
        average_score=stats["average_score"],
        rank=rank or 0
    )


@router.get("/{house_name}/members")
async def get_house_members(
    house_name: str,
    limit: int = 50,
    payload: dict = Depends(main.verify_jwt_token)
):
    """Get house members leaderboard"""
    house = house_name.lower()
    if house not in HOUSES:
        raise HTTPException(status_code=400, detail="Invalid house")
    
    # Get members
    members = [
        {
            "id": u["id"],
            "name": u["name"],
            "email": u["email"],
            "total_score": u.get("total_score", 0),
            "problems_solved": u.get("problems_solved", 0),
            "submissions": u.get("submissions", 0)
        }
        for u in main.users_db.values()
        if u.get("house", "").lower() == house
    ]
    
    # Sort by score
    members.sort(key=lambda x: x["total_score"], reverse=True)
    
    # Add ranks
    for idx, member in enumerate(members[:limit]):
        member["rank"] = idx + 1
    
    return members[:limit]


@router.get("/{house_name}/achievements")
async def get_house_achievements(house_name: str, payload: dict = Depends(main.verify_jwt_token)):
    """Get house-specific achievements"""
    house = house_name.lower()
    if house not in HOUSES:
        raise HTTPException(status_code=400, detail="Invalid house")
    
    # Example achievements
    achievements = {
        "gryffindor": [
            {"id": "brave_1", "name": "First Victory", "description": "Solve your first problem", "icon": "🏆"},
            {"id": "brave_10", "name": "Daring Warrior", "description": "Solve 10 problems", "icon": "⚔️"},
            {"id": "brave_100", "name": "Legend of Gryffindor", "description": "Solve 100 problems", "icon": "👑"}
        ],
        "hufflepuff": [
            {"id": "loyal_1", "name": "First Step", "description": "Solve your first problem", "icon": "🌟"},
            {"id": "loyal_10", "name": "Dedicated Member", "description": "Solve 10 problems", "icon": "💪"},
            {"id": "loyal_100", "name": "Hufflepuff Pride", "description": "Solve 100 problems", "icon": "🏅"}
        ],
        "ravenclaw": [
            {"id": "wise_1", "name": "Knowledge Seeker", "description": "Solve your first problem", "icon": "📚"},
            {"id": "wise_10", "name": "Scholar", "description": "Solve 10 problems", "icon": "🧠"},
            {"id": "wise_100", "name": "Master Mind", "description": "Solve 100 problems", "icon": "🔮"}
        ],
        "slytherin": [
            {"id": "cunning_1", "name": "Rising Star", "description": "Solve your first problem", "icon": "✨"},
            {"id": "cunning_10", "name": "Ambitious Coder", "description": "Solve 10 problems", "icon": "🎯"},
            {"id": "cunning_100", "name": "Slytherin Supreme", "description": "Solve 100 problems", "icon": "💎"}
        ]
    }
    
    return achievements.get(house, [])


@router.get("/colors/theme")
async def get_house_theme(house_name: str, payload: dict = Depends(main.verify_jwt_token)):
    """Get house color theme"""
    house = house_name.lower()
    if house not in HOUSES:
        raise HTTPException(status_code=400, detail="Invalid house")
    
    return {
        "house": house,
        "primary": HOUSES[house]["color"],
        "secondary": HOUSES[house].get("color_light", "#FFFFFF"),
        "emoji": HOUSES[house]["emoji"],
        "name": house.title()
    }


@router.post("/assign-random")
async def assign_random_house_to_user(payload: dict = Depends(main.verify_jwt_token)):
    """Assign a random house (for testing)"""
    user_id = payload.get("sub")
    email = payload.get("email")
    
    user = await main.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    new_house = assign_random_house()
    user["house"] = new_house
    
    # Persist to MongoDB if enabled
    if main.mongo_enabled and main._users_coll is not None:
        await main._users_coll.update_one(
            {"email": email},
            {"$set": {"house": new_house}}
        )
    
    return {
        "message": f"You have been assigned to {new_house.title()}!",
        "house": new_house,
        "emoji": HOUSES[new_house]["emoji"],
        "description": HOUSES[new_house]["description"]
    }
