from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/coding_platform')
db = client['coding_platform']
for u in db.users.find({}, {'email': 1, 'role': 1, '_id': 0}):
    print(f"- {u.get('email')}: {u.get('role')}")
