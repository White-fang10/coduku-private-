"""
CodeHouses - Competitive Coding Platform Backend
Flask + MongoDB + JWT Authentication
"""

import os
import random
import time
import subprocess
import tempfile
import json
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, DESCENDING, ASCENDING
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv

load_dotenv()

# ─── App Setup ───────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "codehouse-secret-key-change-in-prod")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False   # 30-day tokens handled by client

jwt = JWTManager(app)

# ─── Database ────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/coding_platform")
client = MongoClient(MONGO_URI)
db = client.get_default_database() if "coding_platform" not in MONGO_URI.split("/")[-1].split("?")[0] else client["coding_platform"]

# Collections
users_col       = db["users"]
questions_col   = db["questions"]
submissions_col = db["submissions"]
settings_col    = db["settings"]

# Ensure indexes
users_col.create_index("email", unique=True)
questions_col.create_index("difficulty")
submissions_col.create_index([("user_id", ASCENDING), ("submitted_at", DESCENDING)])
submissions_col.create_index("question_id")

# ─── Constants ───────────────────────────────────────────────────────────────
HOUSES = ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"]
DIFFICULTY_FACTORS = {"Easy": 1.0, "Medium": 1.5, "Hard": 2.5}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def serialize(doc):
    """Convert MongoDB ObjectId fields to strings recursively."""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                result[k] = str(v)
            elif isinstance(v, datetime):
                result[k] = v.isoformat()
            elif isinstance(v, (dict, list)):
                result[k] = serialize(v)
            else:
                result[k] = v
        return result
    return doc


def admin_required(fn):
    """Decorator: only allow users with role='admin' or 'teacher'."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = get_jwt_identity()
        user = users_col.find_one({"_id": ObjectId(uid)})
        if not user or user.get("role") not in ["admin", "teacher"]:
            return jsonify({"error": "Admin or Teacher access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def calculate_score(difficulty: str, passed: int, total: int, time_taken: float) -> float:
    """
    Score = Base × Difficulty Factor × Accuracy Bonus × Speed Bonus
    """
    if total == 0:
        return 0.0
    base = 100.0
    diff_factor = DIFFICULTY_FACTORS.get(difficulty, 1.0)
    accuracy = passed / total
    speed_bonus = min(1.2, 1.0 + max(0, (300 - time_taken)) / 1500)
    score = base * diff_factor * accuracy * speed_bonus
    return round(score, 2)


import requests
import concurrent.futures

def _stdin_from_input(inp):
    """Convert a test case input (any type) to a stdin string."""
    import json
    if inp is None or inp == [] or inp == "":
        return ""
    if isinstance(inp, str):
        return inp
    if isinstance(inp, list):
        # List of lines — each element becomes one line
        parts = []
        for item in inp:
            if isinstance(item, list):
                parts.append(" ".join(str(x) for x in item))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(inp)


def run_single_testcase(code, language, inp, expected, func_name, time_limit):
    """
    Executes a single test case using raw stdin/stdout — works for all languages.
    Students write normal programs that read from stdin and print to stdout.
    """
    import subprocess, tempfile

    stdin_data = _stdin_from_input(inp)
    expected_str = str(expected).strip()

    # Detect class name for Java (look for 'public class Foo', fallback to Main)
    def _java_classname(src):
        import re
        m = re.search(r'public\s+class\s+(\w+)', src)
        return m.group(1) if m else "Main"

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:

            if language == "python":
                fpath = os.path.join(tmp_dir, "sol.py")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                run_cmd = ["python", fpath]

            elif language in ("javascript", "js"):
                fpath = os.path.join(tmp_dir, "sol.js")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                run_cmd = ["node", fpath]

            elif language == "java":
                classname = _java_classname(code)
                fpath = os.path.join(tmp_dir, f"{classname}.java")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                cr = subprocess.run(["javac", f"{classname}.java"],
                                    cwd=tmp_dir, capture_output=True, text=True)
                if cr.returncode != 0:
                    return {"input": inp, "expected": expected_str, "actual": "",
                            "passed": False, "error": "Compilation Error: " + cr.stderr.strip()}
                run_cmd = ["java", "-cp", tmp_dir, classname]

            elif language in ("cpp", "c++"):
                fpath = os.path.join(tmp_dir, "sol.cpp")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                out_bin = os.path.join(tmp_dir, "sol.exe")
                cr = subprocess.run(["g++", "-o", out_bin, fpath],
                                    capture_output=True, text=True)
                if cr.returncode != 0:
                    return {"input": inp, "expected": expected_str, "actual": "",
                            "passed": False, "error": "Compilation Error: " + cr.stderr.strip()}
                run_cmd = [out_bin]

            elif language == "c":
                fpath = os.path.join(tmp_dir, "sol.c")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                out_bin = os.path.join(tmp_dir, "sol.exe")
                cr = subprocess.run(["gcc", "-o", out_bin, fpath],
                                    capture_output=True, text=True)
                if cr.returncode != 0:
                    return {"input": inp, "expected": expected_str, "actual": "",
                            "passed": False, "error": "Compilation Error: " + cr.stderr.strip()}
                run_cmd = [out_bin]

            elif language in ("csharp", "c#", "cs"):
                fpath = os.path.join(tmp_dir, "sol.cs")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                out_bin = os.path.join(tmp_dir, "sol.exe")
                cr = subprocess.run(["csc", "-out:" + out_bin, fpath],
                                    capture_output=True, text=True)
                if cr.returncode != 0:
                    return {"input": inp, "expected": expected_str, "actual": "",
                            "passed": False, "error": "Compilation Error: " + cr.stderr.strip()}
                run_cmd = ["mono", out_bin]

            elif language == "go":
                fpath = os.path.join(tmp_dir, "sol.go")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                run_cmd = ["go", "run", fpath]

            elif language == "rust":
                fpath = os.path.join(tmp_dir, "sol.rs")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                out_bin = os.path.join(tmp_dir, "sol")
                cr = subprocess.run(["rustc", "-o", out_bin, fpath],
                                    capture_output=True, text=True)
                if cr.returncode != 0:
                    return {"input": inp, "expected": expected_str, "actual": "",
                            "passed": False, "error": "Compilation Error: " + cr.stderr.strip()}
                run_cmd = [out_bin]

            elif language == "ruby":
                fpath = os.path.join(tmp_dir, "sol.rb")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(code)
                run_cmd = ["ruby", fpath]

            else:
                return {"input": inp, "expected": expected_str, "actual": "",
                        "passed": False,
                        "error": f"Language '{language}' not available in local fallback. Start Docker to enable it."}

            try:
                proc = subprocess.run(
                    run_cmd, input=stdin_data, cwd=tmp_dir,
                    capture_output=True, text=True, timeout=time_limit
                )
                actual = proc.stdout.strip()
                stderr = proc.stderr.strip()

                if proc.returncode != 0:
                    return {"input": inp, "expected": expected_str, "actual": actual,
                            "passed": False, "error": "Runtime Error: " + (stderr or "non-zero exit")}

                passed = actual == expected_str
                return {
                    "input": inp, "expected": expected_str, "actual": actual,
                    "passed": passed,
                    "error": None if passed else f"Expected: {expected_str!r} | Got: {actual!r}"
                }
            except subprocess.TimeoutExpired:
                return {"input": inp, "expected": expected_str, "actual": "",
                        "passed": False, "error": "Time Limit Exceeded"}

    except Exception as e:
        return {"input": inp, "expected": expected_str, "actual": "",
                "passed": False, "error": f"Executor error: {str(e)}"}



def execute_code_external(code: str, language: str, test_cases: list, time_limit: int = 5) -> dict:
    """Execute code against test cases via an external Compiler API concurrently."""
    results = []
    total = len(test_cases)
    passed = 0

    # We use a ThreadPoolExecutor to run all test cases in parallel via the API
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(total, 10)) as executor:
        futures = []
        for tc in test_cases:
            inp = tc.get("input", "")
            expected = tc.get("output", "")
            func_name = tc.get("function_name", "solution")
            futures.append(executor.submit(run_single_testcase, code, language, inp, expected, func_name, time_limit))
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results.append(res)
            if res["passed"]:
                passed += 1

    return {"passed": passed, "total": total, "results": results}


# ─── Auth Routes ─────────────────────────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role_req = (data.get("role") or "student").strip().lower()
    secret   = (data.get("teacher_secret") or "").strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Validate teacher registration
    role = "student"
    if role_req == "teacher":
        expected_secret = os.getenv("TEACHER_SECRET", "pranesh")
        if secret != expected_secret:
            return jsonify({"error": "Invalid teacher access code"}), 403
        role = "teacher"

    if users_col.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    house = random.choice(HOUSES)
    hashed = generate_password_hash(password)
    user_doc = {
        "name": name,
        "email": email,
        "password": hashed,
        "house": house,
        "role": role,
        "problems_solved": 0,
        "total_submissions": 0,
        "average_score": 0.0,
        "total_score": 0.0,
        "created_at": datetime.now(timezone.utc)
    }
    result = users_col.insert_one(user_doc)
    uid = str(result.inserted_id)
    token = create_access_token(identity=uid)

    return jsonify({
        "message": "User registered successfully",
        "access_token": token,
        "user": {
            "id": uid,
            "name": name,
            "email": email,
            "house": house,
            "role": role
        }
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = users_col.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    uid = str(user["_id"])
    token = create_access_token(identity=uid)

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "user": {
            "id": uid,
            "name": user["name"],
            "email": user["email"],
            "house": user["house"],
            "role": user.get("role", "student")
        }
    })


# ─── User Routes ─────────────────────────────────────────────────────────────

@app.route("/api/user/profile", methods=["GET"])
@app.route("/api/user/profile/<target_uid>", methods=["GET"])
@jwt_required()
def get_profile(target_uid=None):
    uid = target_uid if target_uid else get_jwt_identity()
    user = users_col.find_one({"_id": ObjectId(uid)}, {"password": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    subs = list(submissions_col.find({"user_id": uid}, sort=[("submitted_at", DESCENDING)]))
    dates = []
    from datetime import datetime, timezone, timedelta
    for s in subs:
        if "submitted_at" in s:
            date_val = s["submitted_at"]
            if isinstance(date_val, datetime):
                dates.append(date_val.strftime("%Y-%m-%d"))
            else:
                dates.append(str(date_val)[:10])
                
    unique_dates = sorted(list(set(dates)), reverse=True)
    streak = 0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if unique_dates:
        if unique_dates[0] in [today, yesterday]:
            streak = 1
            current_date = datetime.strptime(unique_dates[0], "%Y-%m-%d")
            for i in range(1, len(unique_dates)):
                d = datetime.strptime(unique_dates[i], "%Y-%m-%d")
                if (current_date - d).days == 1:
                    streak += 1
                    current_date = d
                else:
                    break

    badges = []
    
    if streak >= 7:
        badges.append({"id": "week", "name": "Seeker's Spark", "icon": "⚡", "desc": "7 Day Streak"})
    if streak >= 30:
        badges.append({"id": "month", "name": "Marauder's Map", "icon": "🗺️", "desc": "30 Day Streak"})
    if streak >= 365:
        badges.append({"id": "year", "name": "Elder Wand Mastery", "icon": "🪄", "desc": "365 Day Streak"})
        
    top_user = list(users_col.find({"role": "student"}, sort=[("average_score", DESCENDING)], limit=1))
    if top_user and str(top_user[0]["_id"]) == uid and top_user[0].get("average_score", 0) > 0:
        badges.append({"id": "top", "name": "Triwizard Champion", "icon": "🏆", "desc": "Current #1 Global Leader"})
        
    badges.append({"id": "join", "name": "Sorting Hat", "icon": "🎩", "desc": f"Sorted into {user.get('house', 'Hogwarts')}"})

    user["streak"] = streak
    user["badges"] = badges
    user["unlocked_badges"] = user.get("unlocked_badges", [])
    user["claimed_badges"] = user.get("claimed_badges", [])
    
    return jsonify(serialize(user))


@app.route("/api/user/submissions", methods=["GET"])
@jwt_required()
def get_user_submissions():
    uid = get_jwt_identity()
    subs = list(submissions_col.find(
        {"user_id": uid},
        sort=[("submitted_at", DESCENDING)],
        limit=50
    ))
    # Attach question title
    for s in subs:
        try:
            q = questions_col.find_one({"_id": ObjectId(s["question_id"])}, {"title": 1, "difficulty": 1})
            s["question_title"] = q["title"] if q else "Unknown"
            s["difficulty"] = q["difficulty"] if q else "Unknown"
        except Exception:
            s["question_title"] = "Unknown"
            s["difficulty"] = "Unknown"
    return jsonify(serialize(subs))


@app.route("/api/user/set_house", methods=["POST"])
@jwt_required()
def set_house():
    uid = get_jwt_identity()
    data = request.get_json()
    house = data.get("house")
    character_id = data.get("character_id")

    if not house:
        return jsonify({"error": "house is required"}), 400

    update_fields = {"house": house}
    if character_id is not None:
        update_fields["character_id"] = character_id

    result = users_col.update_one(
        {"_id": ObjectId(uid)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "House updated successfully"})


@app.route("/api/user/claim_badge", methods=["POST"])
@jwt_required()
def claim_badge():
    uid = get_jwt_identity()
    data = request.get_json() or {}
    badge_id = data.get("badge_id")
    if not badge_id:
        return jsonify({"error": "No badge ID provided"}), 400
    
    user = users_col.find_one({"_id": ObjectId(uid)})
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    unlocked = user.get("unlocked_badges", [])
    claimed = user.get("claimed_badges", [])
    
    if badge_id not in unlocked:
        return jsonify({"error": "Badge is not unlocked yet"}), 403
    if badge_id in claimed:
        return jsonify({"message": "Badge already claimed"}), 200
        
    users_col.update_one({"_id": ObjectId(uid)}, {"$addToSet": {"claimed_badges": badge_id}})
    return jsonify({"message": "Badge claimed successfully!"}), 200

@app.route("/api/user/update_profile", methods=["POST"])
@jwt_required()
def update_profile():
    uid = get_jwt_identity()
    data = request.get_json()
    name = data.get("name")
    character_id = data.get("character_id")

    update_fields = {}
    if name and name.strip():
        update_fields["name"] = name.strip()
    if character_id is not None:
        update_fields["character_id"] = character_id
        
    if not update_fields:
        return jsonify({"message": "No changes provided"}), 400

    result = users_col.update_one(
        {"_id": ObjectId(uid)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "Profile updated successfully"})


# ─── Question Routes ──────────────────────────────────────────────────────────

@app.route("/api/questions", methods=["GET"])
@jwt_required()
def get_questions():
    filt = {}
    difficulty = request.args.get("difficulty")
    if difficulty:
        filt["difficulty"] = difficulty

    # Security check: students shouldn't see the competition question 
    # unless they are explicitly assigned to it during the time window
    uid = get_jwt_identity()
    user = users_col.find_one({"_id": ObjectId(uid)})
    is_teacher = user and user.get("role") in ["admin", "teacher"]
    
    # Check if a competition is currently set up
    now = datetime.now()
    setting = settings_col.find_one({"key": "competition_question"})
    comp_window_active = False

    if setting and setting.get("value") and not is_teacher:
        comp_id = setting.get("value")
        now_str = datetime.now().strftime("%H:%M")
        start_time = setting.get("start_time", "17:00")
        end_time = setting.get("end_time", "22:00")
        comp_window_active = start_time <= now_str <= end_time
        
        # Hide it by default from normal fetching if window is NOT active
        if not comp_window_active:
            if "_id" not in filt:
                filt["_id"] = {"$ne": ObjectId(comp_id)}
    questions = list(questions_col.find(filt, {"test_cases": 0, "solution": 0}))
    return jsonify(serialize(questions))


@app.route("/api/questions/<question_id>", methods=["GET"])
@jwt_required()
def get_question(question_id):
    try:
        q = questions_col.find_one({"_id": ObjectId(question_id)}, {"solution": 0})
    except InvalidId:
        return jsonify({"error": "Invalid question ID"}), 400
    if not q:
        return jsonify({"error": "Question not found"}), 404

    # Time-gate competition question
    uid = get_jwt_identity()
    user = users_col.find_one({"_id": ObjectId(uid)})
    is_teacher = user and user.get("role") in ["admin", "teacher"]
    
    if not is_teacher:
        setting = settings_col.find_one({"key": "competition_question"})
        if setting and setting.get("value") == question_id:
            now_str = datetime.now().strftime("%H:%M")
            start_time = setting.get("start_time", "17:00")
            end_time = setting.get("end_time", "22:00")
            if not (start_time <= now_str <= end_time):
                return jsonify({"error": f"This trial is only available between {start_time} and {end_time}."}), 403

    # Hide expected output from test cases shown to user
    q_out = serialize(q)
    visible_cases = []
    for tc in q_out.get("test_cases", []):
        visible_cases.append({
            "input": tc.get("input"),
            "function_name": tc.get("function_name", "solution")
        })
    q_out["sample_test_cases"] = visible_cases[:2]   # show first 2
    return jsonify(q_out)


# ─── Submission Routes ────────────────────────────────────────────────────────

@app.route("/api/submit", methods=["POST"])
@jwt_required()
def submit_code():
    uid = get_jwt_identity()
    data = request.get_json()
    question_id = data.get("question_id")
    code        = data.get("code", "")
    language    = data.get("language", "python").lower()

    if not question_id or not code:
        return jsonify({"error": "question_id and code are required"}), 400

    try:
        q = questions_col.find_one({"_id": ObjectId(question_id)})
    except InvalidId:
        return jsonify({"error": "Invalid question ID"}), 400
    if not q:
        return jsonify({"error": "Question not found"}), 404

    if language not in ["c", "cpp", "java", "javascript", "python", "go", "rust", "ruby", "csharp"]:
        return jsonify({"error": f"{language} is not supported at this time"}), 400

    start = time.time()
    exec_result = execute_code_external(code, language, q.get("test_cases", []), q.get("time_limit", 5))
    elapsed = round(time.time() - start, 3)

    passed = exec_result["passed"]
    total  = exec_result["total"]
    score  = calculate_score(q["difficulty"], passed, total, elapsed)

    # Compute /10 visible score for the popup
    correctness_10 = round((passed / max(total, 1)) * 7.0, 1)
    visible_score  = round(min(10.0, correctness_10), 1)
    verdict = "Accepted" if passed == total and total > 0 else ("Partially Correct" if passed > 0 else "Wrong Answer")

    # Save submission
    sub_doc = {
        "user_id":        uid,
        "question_id":    str(q["_id"]),
        "code":           code,
        "language":       language,
        "score":          score,
        "passed_tests":   passed,
        "total_tests":    total,
        "execution_time": elapsed,
        "exec_results":   exec_result["results"],
        "submitted_at":   datetime.now(timezone.utc)
    }
    sub_result = submissions_col.insert_one(sub_doc)

    # Update user stats
    user = users_col.find_one({"_id": ObjectId(uid)})
    if user:
        pipeline = [
            {"$match": {"user_id": uid}},
            {"$group": {
                "_id": "$question_id",
                "max_score": {"$max": "$score"},
                "is_solved": {
                    "$max": {
                        "$cond": [
                            {"$and": [{"$gt": ["$passed_tests", 0]}, {"$gt": ["$total_tests", 0]}]},
                            1,
                            0
                        ]
                    }
                }
            }}
        ]
        stats = list(submissions_col.aggregate(pipeline))
        
        unique_attempts = len(stats)
        total_score = sum(item.get("max_score", 0) for item in stats)
        avg_score = round(total_score / unique_attempts, 2) if unique_attempts > 0 else 0.0
        solved = sum(item.get("is_solved", 0) for item in stats)

        users_col.update_one(
            {"_id": ObjectId(uid)},
            {"$set": {
                "total_submissions": unique_attempts,
                "total_score": total_score,
                "average_score": avg_score,
                "problems_solved": solved
            }}
        )

    return jsonify({
        "submission_id":  str(sub_result.inserted_id),
        "score":          visible_score,          # /10 for popup
        "legacy_score":   score,                  # old scale for leaderboard
        "passed_tests":   passed,
        "total_tests":    total,
        "execution_time": elapsed,
        "verdict":        verdict,
        "execution_result": exec_result["results"],
        "score_breakdown": {
            "correctness":   correctness_10,
            "time_bonus":    0.0,
            "memory_bonus":  0.0,
            "visible_score": visible_score,
        }
    })


@app.route("/api/execute", methods=["POST"])
@jwt_required()
def execute_standalone():
    """Run code with optional stdin — supports Python, JS, Java, C++, C, Go, Rust, Ruby, C#."""
    import subprocess, tempfile, re
    data     = request.get_json()
    code     = data.get("code", "")
    language = data.get("language", "python").lower()
    stdin    = data.get("stdin", "")

    def _java_classname(src):
        m = re.search(r'public\s+class\s+(\w+)', src)
        return m.group(1) if m else "Main"

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:

            if language == "python":
                fpath = os.path.join(tmp_dir, "sol.py")
                open(fpath, "w", encoding="utf-8").write(code)
                run_cmd = ["python", fpath]

            elif language in ("javascript", "js"):
                fpath = os.path.join(tmp_dir, "sol.js")
                open(fpath, "w", encoding="utf-8").write(code)
                run_cmd = ["node", fpath]

            elif language == "java":
                classname = _java_classname(code)
                fpath = os.path.join(tmp_dir, f"{classname}.java")
                open(fpath, "w", encoding="utf-8").write(code)
                cr = subprocess.run(["javac", f"{classname}.java"],
                                    cwd=tmp_dir, capture_output=True, text=True)
                if cr.returncode != 0:
                    return jsonify({"stdout": "", "stderr": cr.stderr, "error": "Compilation Error"})
                run_cmd = ["java", "-cp", tmp_dir, classname]

            elif language in ("cpp", "c++"):
                fpath = os.path.join(tmp_dir, "sol.cpp")
                open(fpath, "w", encoding="utf-8").write(code)
                out = os.path.join(tmp_dir, "sol.exe")
                cr = subprocess.run(["g++", "-o", out, fpath], capture_output=True, text=True)
                if cr.returncode != 0:
                    return jsonify({"stdout": "", "stderr": cr.stderr, "error": "Compilation Error"})
                run_cmd = [out]

            elif language == "c":
                fpath = os.path.join(tmp_dir, "sol.c")
                open(fpath, "w", encoding="utf-8").write(code)
                out = os.path.join(tmp_dir, "sol.exe")
                cr = subprocess.run(["gcc", "-o", out, fpath], capture_output=True, text=True)
                if cr.returncode != 0:
                    return jsonify({"stdout": "", "stderr": cr.stderr, "error": "Compilation Error"})
                run_cmd = [out]

            elif language == "go":
                fpath = os.path.join(tmp_dir, "sol.go")
                open(fpath, "w", encoding="utf-8").write(code)
                run_cmd = ["go", "run", fpath]

            elif language == "rust":
                fpath = os.path.join(tmp_dir, "sol.rs")
                open(fpath, "w", encoding="utf-8").write(code)
                out = os.path.join(tmp_dir, "sol")
                cr = subprocess.run(["rustc", "-o", out, fpath], capture_output=True, text=True)
                if cr.returncode != 0:
                    return jsonify({"stdout": "", "stderr": cr.stderr, "error": "Compilation Error"})
                run_cmd = [out]

            elif language == "ruby":
                fpath = os.path.join(tmp_dir, "sol.rb")
                open(fpath, "w", encoding="utf-8").write(code)
                run_cmd = ["ruby", fpath]

            elif language in ("csharp", "c#", "cs"):
                fpath = os.path.join(tmp_dir, "sol.cs")
                open(fpath, "w", encoding="utf-8").write(code)
                out = os.path.join(tmp_dir, "sol.exe")
                cr = subprocess.run(["csc", "-out:" + out, fpath], capture_output=True, text=True)
                if cr.returncode != 0:
                    return jsonify({"stdout": "", "stderr": cr.stderr, "error": "Compilation Error"})
                run_cmd = ["mono", out]

            else:
                return jsonify({"stdout": "", "stderr": "",
                                "error": f"'{language}' not available locally. Start Docker to enable it."})

            proc = subprocess.run(run_cmd, input=stdin, cwd=tmp_dir,
                                  capture_output=True, text=True, timeout=10)
            return jsonify({
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "error": None if proc.returncode == 0 else "Runtime Error"
            })

    except subprocess.TimeoutExpired:
        return jsonify({"stdout": "", "stderr": "Time Limit Exceeded", "error": "Timeout"})
    except Exception as e:
        return jsonify({"stdout": "", "stderr": str(e), "error": "System Error"})


# ─── Leaderboard Routes ───────────────────────────────────────────────────────

@app.route("/api/leaderboards/global", methods=["GET"])
@jwt_required()
def global_leaderboard():
    # Check if competition mode is active
    now_str = datetime.now().strftime("%H:%M")
    setting = settings_col.find_one({"key": "competition_question"})
    
    comp_active = False
    comp_q_id = None
    if setting:
        start_time = setting.get("start_time", "17:00")
        end_time = setting.get("end_time", "22:00")
        comp_active = start_time <= now_str <= end_time
        comp_q_id = setting.get("value")

    if comp_active and comp_q_id:
        # Calculate ranks based ONLY on the competition question
        pipeline = [
            {"$match": {"question_id": comp_q_id}},
            {"$group": {
                "_id": "$user_id",
                "max_score": {"$max": "$score"},
                "solved": {"$first": 1}
            }},
            {"$sort": {"max_score": DESCENDING}}
        ]
        comp_results = list(submissions_col.aggregate(pipeline))
        comp_map = {res["_id"]: res["max_score"] for res in comp_results}
        
        students = list(users_col.find({"role": "student"}, {"password": 0}))
        result = []
        for s in students:
            uid = str(s["_id"])
            if uid in comp_map:
                result.append({
                    "id": uid,
                    "name": s["name"],
                    "house": s.get("house", ""),
                    "average_score": comp_map[uid],
                    "problems_solved": 1,
                    "submissions": 1
                })
        # Sort and rank
        result.sort(key=lambda x: x["average_score"], reverse=True)
        for i, r in enumerate(result, 1):
            r["rank"] = i
        return jsonify(result)

    # Standard global leaderboard
    students = list(users_col.find(
        {"role": "student"},
        {"password": 0},
        sort=[("average_score", DESCENDING)],
        limit=100
    ))
    result = []
    for i, s in enumerate(students, 1):
        result.append({
            "rank": i,
            "id": str(s["_id"]),
            "name": s["name"],
            "house": s.get("house", ""),
            "average_score": s.get("average_score", 0.0),
            "problems_solved": s.get("problems_solved", 0),
            "submissions": s.get("total_submissions", 0)
        })
    return jsonify(result)


@app.route("/api/leaderboards/houses", methods=["GET"])
@jwt_required()
def house_leaderboard():
    # Check if competition mode is active
    now_str = datetime.now().strftime("%H:%M")
    setting = settings_col.find_one({"key": "competition_question"})
    
    comp_active = False
    comp_q_id = None
    if setting:
        start_time = setting.get("start_time", "17:00")
        end_time = setting.get("end_time", "22:00")
        comp_active = start_time <= now_str <= end_time
        comp_q_id = setting.get("value")

    house_data = {}
    for house in HOUSES:
        members = list(users_col.find({"house": house, "role": "student"}))
        if not members:
            avg = 0.0
        else:
            if comp_active and comp_q_id:
                # Average only for the competition question
                m_ids = [str(m["_id"]) for m in members]
                pipeline = [
                    {"$match": {"user_id": {"$in": m_ids}, "question_id": comp_q_id}},
                    {"$group": {"_id": "$user_id", "best": {"$max": "$score"}}}
                ]
                scores = list(submissions_col.aggregate(pipeline))
                if not scores:
                    avg = 0.0
                else:
                    avg = round(sum(s["best"] for s in scores) / len(members), 2)
            else:
                total = sum(m.get("average_score", 0.0) for m in members)
                avg = round(total / len(members), 2)
        
        house_data[house] = {
            "house": house,
            "average_score": avg,
            "members": len(members),
            "total_score": round(avg * len(members), 2) # simplified
        }

    sorted_houses = sorted(house_data.values(), key=lambda x: x["average_score"], reverse=True)
    for i, h in enumerate(sorted_houses, 1):
        h["rank"] = i
    return jsonify(sorted_houses)


@app.route("/api/leaderboards/house/<house_name>", methods=["GET"])
@jwt_required()
def house_members_leaderboard(house_name):
    if house_name not in HOUSES:
        return jsonify({"error": f"Unknown house: {house_name}"}), 400
    members = list(users_col.find(
        {"house": house_name, "role": "student"},
        {"password": 0},
        sort=[("average_score", DESCENDING)]
    ))
    result = []
    for i, m in enumerate(members, 1):
        result.append({
            "rank": i,
            "id": str(m["_id"]),
            "name": m["name"],
            "average_score": m.get("average_score", 0.0),
            "problems_solved": m.get("problems_solved", 0),
            "submissions": m.get("total_submissions", 0)
        })
    return jsonify(result)


# ─── Houses Route ─────────────────────────────────────────────────────────────

@app.route("/api/houses", methods=["GET"])
@jwt_required()
def get_houses():
    result = []
    for house in HOUSES:
        members = list(users_col.find({"house": house, "role": "student"}))
        avg = 0.0
        if members:
            total = sum(m.get("average_score", 0.0) for m in members)
            avg = round(total / len(members), 2)
        result.append({
            "name": house,
            "members": len(members),
            "average_score": avg
        })
    return jsonify(result)


# ─── Admin Routes ─────────────────────────────────────────────────────────────

@app.route("/api/admin/questions", methods=["POST"])
@admin_required
def create_question():
    data = request.get_json()
    title       = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    difficulty  = data.get("difficulty", "Easy")
    test_cases  = data.get("test_cases", [])
    solution    = data.get("solution", "")
    time_limit  = int(data.get("time_limit", 5))
    memory_limit = int(data.get("memory_limit", 256))

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400
    if difficulty not in DIFFICULTY_FACTORS:
        return jsonify({"error": f"Difficulty must be one of {list(DIFFICULTY_FACTORS.keys())}"}), 400
    if not test_cases:
        return jsonify({"error": "At least one test case is required"}), 400

    q_doc = {
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "test_cases": test_cases,
        "solution": solution,
        "time_limit": time_limit,
        "memory_limit": memory_limit,
        "created_at": datetime.now(timezone.utc)
    }
    result = questions_col.insert_one(q_doc)
    q_doc["_id"] = str(result.inserted_id)
    return jsonify(serialize(q_doc)), 201


@app.route("/api/admin/questions/<question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    try:
        q = questions_col.find_one({"_id": ObjectId(question_id)})
    except InvalidId:
        return jsonify({"error": "Invalid question ID"}), 400
    if not q:
        return jsonify({"error": "Question not found"}), 404

    data = request.get_json()
    update_fields = {}
    for field in ["title", "description", "difficulty", "test_cases", "solution", "time_limit", "memory_limit"]:
        if field in data:
            update_fields[field] = data[field]

    if "difficulty" in update_fields and update_fields["difficulty"] not in DIFFICULTY_FACTORS:
        return jsonify({"error": "Invalid difficulty"}), 400

    questions_col.update_one({"_id": ObjectId(question_id)}, {"$set": update_fields})
    updated = questions_col.find_one({"_id": ObjectId(question_id)}, {"solution": 0})
    return jsonify(serialize(updated))


@app.route("/api/admin/submissions", methods=["GET"])
@admin_required
def admin_submissions():
    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    skip  = (page - 1) * limit

    subs = list(submissions_col.find(
        {},
        sort=[("submitted_at", DESCENDING)],
        skip=skip, limit=limit
    ))
    for s in subs:
        try:
            user = users_col.find_one({"_id": ObjectId(s["user_id"])}, {"name": 1, "house": 1})
            s["user_name"]  = user["name"] if user else "Unknown"
            s["user_house"] = user.get("house", "") if user else ""
        except Exception:
            s["user_name"] = "Unknown"
            s["user_house"] = ""
        try:
            q = questions_col.find_one({"_id": ObjectId(s["question_id"])}, {"title": 1, "difficulty": 1})
            s["question_title"] = q["title"] if q else "Unknown"
            s["question_diff"]  = q["difficulty"] if q else "Unknown"
        except Exception:
            s["question_title"] = "Unknown"
            s["question_diff"]  = "Unknown"

    total = submissions_col.count_documents({})
    return jsonify({
        "submissions": serialize(subs),
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    })


@app.route("/api/admin/users", methods=["GET"])
@admin_required
def admin_users():
    result = list(users_col.find({}, {"password": 0}, sort=[("created_at", DESCENDING)]))
    return jsonify(serialize(result))


@app.route("/api/admin/competition", methods=["GET", "POST"])
@admin_required
def manage_competition():
    if request.method == "POST":
        data = request.get_json()
        q_id = data.get("question_id")
        start_time = data.get("start_time", "17:00")
        end_time = data.get("end_time", "22:00")
        settings_col.update_one(
            {"key": "competition_question"},
            {"$set": {"value": q_id, "start_time": start_time, "end_time": end_time}},
            upsert=True
        )
        return jsonify({"message": "Competition question updated successfully"})
    
    res = settings_col.find_one({"key": "competition_question"})
    return jsonify({"question_id": res["value"] if res else None})


@app.route("/api/competition/status", methods=["GET"])
def competition_status():
    now_str = datetime.now().strftime("%H:%M")
    res = settings_col.find_one({"key": "competition_question"})
    start_time = res.get("start_time", "17:00") if res else "17:00"
    end_time = res.get("end_time", "22:00") if res else "22:00"
    # active = start_time <= now_str <= end_time
    # Paused for project work as requested by user
    active = False
    return jsonify({
        "active": active,
        "question_id": res["value"] if res else None,
        "current_time": now_str,
        "start_time": start_time,
        "end_time": end_time
    })


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "CodeHouses API",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    port  = int(os.getenv("PORT", 5000))
    print(f"🚀 CodeHouses API starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
