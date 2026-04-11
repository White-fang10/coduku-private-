from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

# In a true microservice, this would have its own database connection.
# For our decomposed monolith, we import the shared data layers.
import main

router = APIRouter(prefix="/api/v1/leaderboards", tags=["leaderboard"])

@router.get("/global")
async def global_leaderboard(payload: dict = Depends(main.verify_jwt_token)):
    if main.redis_enabled:
        z = await main.redis_get_leaderboard_global(limit=50)
        ordered_emails = [m for (m, _) in z]
        users_list = [main.users_db[email] for email in ordered_emails if email in main.users_db]
    else:
        users_list = await main.get_leaderboard_users_sorted()
    
    return [
        {
            "rank": idx + 1,
            "name": user["name"],
            "house": user.get("house", "gryffindor").title(),
            "score": user.get("total_score", 0),
            "problems_solved": user.get("problems_solved", 0),
            "submissions": user.get("submissions", 0)
        }
        for idx, user in enumerate(users_list)
    ]

@router.get("/houses")
async def house_leaderboards(payload: dict = Depends(main.verify_jwt_token)):
    houses = {
        "gryffindor": {"members": 0, "total_score": 0, "avg_score": 0},
        "hufflepuff": {"members": 0, "total_score": 0, "avg_score": 0},
        "ravenclaw": {"members": 0, "total_score": 0, "avg_score": 0},
        "slytherin": {"members": 0, "total_score": 0, "avg_score": 0}
    }

    if main.redis_enabled and main._redis_client is not None:
        for house_name in houses.keys():
            zset = f"coduku:lb:house:{house_name}"
            entries = await main._redis_client.zrevrange(zset, 0, -1, withscores=True)
            houses[house_name]["members"] = len(entries)
            houses[house_name]["total_score"] = sum(int(score) for (_email, score) in entries)
            members = houses[house_name]["members"]
            total = houses[house_name]["total_score"]
            houses[house_name]["avg_score"] = total / members if members > 0 else 0
    else:
        users_list = await main.get_leaderboard_users_sorted()
        for user in users_list:
            house = user.get("house", "gryffindor")
            score = user.get("total_score", 0)
            houses[house]["members"] += 1
            houses[house]["total_score"] += score

        for house in houses:
            members = houses[house]["members"]
            total = houses[house]["total_score"]
            houses[house]["avg_score"] = total / members if members > 0 else 0
    
    return [
        {
            "rank": idx + 1,
            "house": house.title(),
            "total_score": data["total_score"],
            "members": data["members"],
            "average_score": round(data["avg_score"], 2)
        }
        for idx, (house, data) in enumerate(sorted(
            houses.items(),
            key=lambda x: x[1]["total_score"],
            reverse=True
        ))
    ]

@router.get("/house/{house_name}")
async def house_members(house_name: str, payload: dict = Depends(main.verify_jwt_token)):
    house = house_name.lower()
    valid_houses = ["gryffindor", "hufflepuff", "ravenclaw", "slytherin"]
    
    if house not in valid_houses:
        raise HTTPException(status_code=400, detail="Invalid house")
    
    if main.redis_enabled and main._redis_client is not None:
        zset = f"coduku:lb:house:{house}"
        entries = await main._redis_client.zrevrange(zset, 0, -1, withscores=True)
        members = []
        for (email, score) in entries:
            u = main.users_db.get(email)
            if not u:
                continue
            members.append({**u, "total_score": int(score)})
    else:
        users_list = await main.get_leaderboard_users_sorted()
        members = sorted(
            [u for u in users_list if u.get("house", "gryffindor") == house],
            key=lambda x: x.get("total_score", 0),
            reverse=True
        )
    
    return [
        {
            "rank": idx + 1,
            "name": member["name"],
            "score": member.get("total_score", 0),
            "problems_solved": member.get("problems_solved", 0)
        }
        for idx, member in enumerate(members)
    ]
