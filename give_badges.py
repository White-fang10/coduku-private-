from pymongo import MongoClient
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["coding_platform"]
users_col = db["users"]

user = users_col.find_one({"email": "esppranesh@gmail.com"})
if user:
    print(f"Found user: {user['_id']}")
    # Give all badges in BADGE_CATEGORIES to the user
    badges = [
        "streak_3", "streak_7", "streak_14", "streak_30", "streak_60", "streak_100",
        "perf_speed", "perf_lightning", "perf_complexity", "perf_efficiency", "perf_perfection",
        "vol_1", "vol_10", "vol_50", "vol_100", "vol_250", "vol_500", "vol_1000",
        "comp_elite", "comp_champion", "comp_conqueror", "comp_undisputed",
        "battle_first", "battle_10", "battle_streak", "battle_unstoppable",
        "debug_first", "debug_10", "debug_complex", "debug_clean",
        "rare_night", "rare_weekend", "rare_phoenix", "rare_edge", "rare_veil",
        "house_loyal", "house_pillar", "house_chosen"
    ]
    users_col.update_one({"_id": user["_id"]}, {"$set": {"unlocked_badges": badges}})
    print("Updated user with all badges.")
else:
    print("User not found.")
