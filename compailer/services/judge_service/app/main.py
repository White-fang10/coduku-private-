"""
CODUKU Judge Service - Production Ready
Handles code submission evaluation, Judge0 integration, and leaderboard updates.
Supports 13+ programming languages with detailed test case feedback.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import asyncio
import logging
import os
import re
from enum import Enum
from datetime import datetime
import json
import uuid
from app.services.output_normalizer import OutputNormalizer
from app.services.database_service import DatabaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CODUKU Judge Service",
    description="Code submission evaluation and language compilation service",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= CONFIGURATION =============
JUDGE0_URL = os.getenv("JUDGE0_URL", "http://judge0:2358")
LEADERBOARD_URL = os.getenv("LEADERBOARD_URL", "http://leaderboard:8003")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY", "")


@app.on_event("startup")
async def startup():
    await DatabaseService.initialize()


# Language ID mappings (Judge0 official IDs)
# Note: Java, Go, JavaScript/Node12 do NOT work on WSL2 due to kernel sandbox limitations
# Working: Python, C, C++, Rust, Ruby, C#, PHP, TypeScript(Deno), Kotlin(limited)
LANGUAGE_IDS = {
    "python": 71,
    "python3": 71,
    "c": 50,
    "cpp": 54,
    "cpp17": 54,
    "c++": 54,
    "rust": 73,
    "ruby": 72,
    "csharp": 51,
    "c#": 51,
    "cs": 51,
    "php": 68,
    # These work but may be slow on WSL2:
    "typescript": 74,
    "ts": 74,
    "kotlin": 78,
    # These have WSL2 kernel issues — kept for Docker-native Linux deployments:
    "java": 62,
    "javascript": 63,
    "js": 63,
    "node": 63,
    "go": 60,
}

# ============= DATA MODELS =============

class VerdictEnum(str, Enum):
    """Submission verdict status codes"""
    ACCEPTED = "Accepted"
    WRONG_ANSWER = "Wrong Answer"
    RUNTIME_ERROR = "Runtime Error"
    TIME_LIMIT = "Time Limit Exceeded"
    COMPILATION_ERROR = "Compilation Error"
    PARTIAL = "Partially Correct"
    PENDING = "Pending"


class TestCaseResult(BaseModel):
    """Individual test case result"""
    test_case_number: int
    input: str
    expected_output: str
    actual_output: str
    passed: bool
    runtime_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    error: Optional[str] = None


class ScoreBreakdown(BaseModel):
    """Visible /10 score shown to the user after every submission"""
    correctness: float       # 0–7.0  (passed/total × 7)
    time_bonus: float        # 0–1.5
    memory_bonus: float      # 0–1.5
    visible_score: float     # sum, capped at 10.0
    max_score: float = 10.0
    # Hidden leaderboard components
    first_solve_bonus: float = 0.0   # +15 for first 5 solvers
    streak_bonus: float = 0.0        # +5 per day streak (max +25)
    wrong_attempt_penalty: float = 0.0  # −2 per WA before AC
    leaderboard_points: float = 0.0  # total hidden points sent to leaderboard


class SubmissionResult(BaseModel):
    """Complete submission evaluation result"""
    submission_id: str
    verdict: VerdictEnum
    total_test_cases: int
    passed_test_cases: int
    language: str
    runtime_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    compilation_error: Optional[str] = None
    test_cases: List[TestCaseResult]
    score: float              # visible /10 score
    score_breakdown: Optional[ScoreBreakdown] = None
    submitted_code: str
    submission_time: str


class ProblemExample(BaseModel):
    """Example input/output for a problem"""
    input: str
    output: str
    explanation: Optional[str] = None


class TestCase(BaseModel):
    """Test case for a problem"""
    input: str
    expected_output: str


class Problem(BaseModel):
    """Coding problem definition"""
    id: int
    title: str
    description: str
    difficulty: str  # Easy, Medium, Hard
    points: int  # Points awarded on "Accepted"
    examples: List[ProblemExample]
    test_cases: List[TestCase]
    constraints: str
    time_limit_seconds: int
    memory_limit_mb: int


class SubmissionRequest(BaseModel):
    """Submission payload"""
    problem_id: int
    language: str
    code: str
    user_id: str
    username: str
    house: str
    prior_wrong_attempts: int = 0
    streak_days: int = 0


class RunSubmissionRequest(BaseModel):
    """Request to run code on specific test cases"""
    problem_id: int
    language: str
    code: str
    test_cases: List[Dict[str, str]] = None  # Override test cases



# ============= PROBLEM BANK =============

PROBLEMS: Dict[int, Problem] = {

    # ── EASY ──────────────────────────────────────────────────────────────────

    1: Problem(
        id=1, title="Hello World", difficulty="Easy", points=5,
        description="Print the text: Hello, World!\n\nNo input is given.\n\nExample:\nOutput: Hello, World!",
        constraints="No input.",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[ProblemExample(input="(none)", output="Hello, World!")],
        test_cases=[
            TestCase(input="", expected_output="Hello, World!"),
        ],
    ),

    2: Problem(
        id=2, title="Sum of Two Numbers", difficulty="Easy", points=8,
        description=(
            "Read two integers from one line (space-separated) and print their sum.\n\n"
            "Example:\nInput: 3 5\nOutput: 8"
        ),
        constraints="-10^9 <= a, b <= 10^9",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="3 5", output="8"),
            ProblemExample(input="-1 1", output="0"),
        ],
        test_cases=[
            TestCase(input="3 5",       expected_output="8"),
            TestCase(input="-1 1",      expected_output="0"),
            TestCase(input="0 0",       expected_output="0"),
            TestCase(input="100 200",   expected_output="300"),
            TestCase(input="-50 -50",   expected_output="-100"),
        ],
    ),

    3: Problem(
        id=3, title="Reverse a String", difficulty="Easy", points=8,
        description=(
            "Read a string and print it reversed.\n\n"
            "Example:\nInput: hello\nOutput: olleh"
        ),
        constraints="1 <= len(s) <= 10^5",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="hello", output="olleh"),
            ProblemExample(input="abcde", output="edcba"),
        ],
        test_cases=[
            TestCase(input="hello",   expected_output="olleh"),
            TestCase(input="abcde",   expected_output="edcba"),
            TestCase(input="a",       expected_output="a"),
            TestCase(input="racecar", expected_output="racecar"),
            TestCase(input="Python",  expected_output="nohtyP"),
        ],
    ),

    4: Problem(
        id=4, title="Even or Odd", difficulty="Easy", points=8,
        description=(
            "Given an integer n, print 'Even' if it is even, 'Odd' otherwise.\n\n"
            "Example:\nInput: 4\nOutput: Even"
        ),
        constraints="-10^9 <= n <= 10^9",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="4", output="Even"),
            ProblemExample(input="7", output="Odd"),
        ],
        test_cases=[
            TestCase(input="4",  expected_output="Even"),
            TestCase(input="7",  expected_output="Odd"),
            TestCase(input="0",  expected_output="Even"),
            TestCase(input="-5", expected_output="Odd"),
            TestCase(input="-2", expected_output="Even"),
        ],
    ),

    5: Problem(
        id=5, title="Count Vowels", difficulty="Easy", points=10,
        description=(
            "Given a string, count the number of vowels (a, e, i, o, u — case-insensitive).\n\n"
            "Example:\nInput: Hello World\nOutput: 3"
        ),
        constraints="1 <= len(s) <= 10^5",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="Hello World", output="3"),
            ProblemExample(input="aeiou",       output="5"),
        ],
        test_cases=[
            TestCase(input="Hello World",  expected_output="3"),
            TestCase(input="aeiou",        expected_output="5"),
            TestCase(input="rhythm",       expected_output="0"),
            TestCase(input="Programming",  expected_output="3"),
            TestCase(input="AEIOU",        expected_output="5"),
        ],
    ),

    6: Problem(
        id=6, title="FizzBuzz", difficulty="Easy", points=10,
        description=(
            "Given n, print numbers 1 to n one per line.\n"
            "- Multiples of 3: print Fizz\n"
            "- Multiples of 5: print Buzz\n"
            "- Multiples of both: print FizzBuzz\n"
            "- Otherwise: print the number\n\n"
            "Example:\nInput: 5\nOutput:\n1\n2\nFizz\n4\nBuzz"
        ),
        constraints="1 <= n <= 10^4",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="5",  output="1\n2\nFizz\n4\nBuzz"),
            ProblemExample(input="15", output="1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"),
        ],
        test_cases=[
            TestCase(input="1",  expected_output="1"),
            TestCase(input="3",  expected_output="1\n2\nFizz"),
            TestCase(input="5",  expected_output="1\n2\nFizz\n4\nBuzz"),
            TestCase(input="15", expected_output="1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"),
        ],
    ),

    7: Problem(
        id=7, title="Fibonacci Number", difficulty="Easy", points=10,
        description=(
            "Given n, print the nth Fibonacci number.\n"
            "F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)\n\n"
            "Example:\nInput: 6\nOutput: 8"
        ),
        constraints="0 <= n <= 30",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="6",  output="8"),
            ProblemExample(input="10", output="55"),
        ],
        test_cases=[
            TestCase(input="0",  expected_output="0"),
            TestCase(input="1",  expected_output="1"),
            TestCase(input="6",  expected_output="8"),
            TestCase(input="10", expected_output="55"),
            TestCase(input="20", expected_output="6765"),
        ],
    ),

    8: Problem(
        id=8, title="Palindrome Check", difficulty="Easy", points=10,
        description=(
            "Given a string, print 'true' if it is a palindrome, 'false' otherwise.\n"
            "Ignore spaces and case.\n\n"
            "Example:\nInput: racecar\nOutput: true"
        ),
        constraints="1 <= len(s) <= 10^5",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="racecar", output="true"),
            ProblemExample(input="hello",   output="false"),
        ],
        test_cases=[
            TestCase(input="racecar",                    expected_output="true"),
            TestCase(input="hello",                      expected_output="false"),
            TestCase(input="A man a plan a canal Panama", expected_output="true"),
            TestCase(input="Was it a car or a cat I saw", expected_output="true"),
            TestCase(input="python",                     expected_output="false"),
        ],
    ),

    # ── MEDIUM ────────────────────────────────────────────────────────────────

    9: Problem(
        id=9, title="Two Sum", difficulty="Medium", points=20,
        description=(
            "Given an array of integers and a target, print the 0-based indices of the two numbers "
            "that add up to the target (space-separated). Exactly one solution exists.\n\n"
            "Input:\nLine 1: space-separated integers\nLine 2: target\n\n"
            "Example:\nInput:\n2 7 11 15\n9\nOutput: 0 1"
        ),
        constraints="2 <= n <= 10^4, -10^9 <= nums[i] <= 10^9",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="2 7 11 15\n9", output="0 1"),
            ProblemExample(input="3 2 4\n6",     output="1 2"),
        ],
        test_cases=[
            TestCase(input="2 7 11 15\n9", expected_output="0 1"),
            TestCase(input="3 2 4\n6",     expected_output="1 2"),
            TestCase(input="3 3\n6",       expected_output="0 1"),
            TestCase(input="1 5 3 7\n8",   expected_output="1 2"),
            TestCase(input="2 5 5 11\n10", expected_output="1 2"),
        ],
    ),

    10: Problem(
        id=10, title="Valid Parentheses", difficulty="Medium", points=20,
        description=(
            "Given a string of brackets '(', ')', '{', '}', '[', ']', "
            "print 'true' if valid, 'false' otherwise.\n"
            "Valid means every open bracket is closed in the correct order.\n\n"
            "Example:\nInput: ()[]{}\nOutput: true"
        ),
        constraints="1 <= len(s) <= 10^4",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="()[]{}", output="true"),
            ProblemExample(input="(]",     output="false"),
        ],
        test_cases=[
            TestCase(input="()[]{}",  expected_output="true"),
            TestCase(input="(]",      expected_output="false"),
            TestCase(input="([)]",    expected_output="false"),
            TestCase(input="{[]}",    expected_output="true"),
            TestCase(input="((((",    expected_output="false"),
        ],
    ),

    11: Problem(
        id=11, title="Factorial", difficulty="Medium", points=15,
        description=(
            "Given n, print n! (factorial).\n\n"
            "Example:\nInput: 5\nOutput: 120"
        ),
        constraints="0 <= n <= 12",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="5",  output="120"),
            ProblemExample(input="10", output="3628800"),
        ],
        test_cases=[
            TestCase(input="0",  expected_output="1"),
            TestCase(input="1",  expected_output="1"),
            TestCase(input="5",  expected_output="120"),
            TestCase(input="10", expected_output="3628800"),
            TestCase(input="12", expected_output="479001600"),
        ],
    ),

    12: Problem(
        id=12, title="Prime Check", difficulty="Medium", points=20,
        description=(
            "Given n, print 'Prime' if it is prime, 'Not Prime' otherwise.\n\n"
            "Example:\nInput: 17\nOutput: Prime"
        ),
        constraints="2 <= n <= 10^6",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="17", output="Prime"),
            ProblemExample(input="4",  output="Not Prime"),
        ],
        test_cases=[
            TestCase(input="2",   expected_output="Prime"),
            TestCase(input="17",  expected_output="Prime"),
            TestCase(input="4",   expected_output="Not Prime"),
            TestCase(input="97",  expected_output="Prime"),
            TestCase(input="100", expected_output="Not Prime"),
        ],
    ),

    13: Problem(
        id=13, title="Maximum Subarray", difficulty="Medium", points=20,
        description=(
            "Given an array of integers (space-separated), find the contiguous subarray "
            "with the largest sum and print that sum.\n\n"
            "Example:\nInput: -2 1 -3 4 -1 2 1 -5 4\nOutput: 6"
        ),
        constraints="1 <= n <= 10^5, -10^4 <= nums[i] <= 10^4",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="-2 1 -3 4 -1 2 1 -5 4", output="6"),
            ProblemExample(input="5 4 -1 7 8",             output="23"),
        ],
        test_cases=[
            TestCase(input="-2 1 -3 4 -1 2 1 -5 4", expected_output="6"),
            TestCase(input="1",                      expected_output="1"),
            TestCase(input="5 4 -1 7 8",             expected_output="23"),
            TestCase(input="-1 -2 -3",               expected_output="-1"),
            TestCase(input="2 -1 2 3 4 -5",          expected_output="10"),
        ],
    ),

    14: Problem(
        id=14, title="Binary Search", difficulty="Medium", points=20,
        description=(
            "Given a sorted array of distinct integers and a target, print the 0-based index "
            "of the target. Print -1 if not found.\n\n"
            "Input:\nLine 1: space-separated sorted integers\nLine 2: target\n\n"
            "Example:\nInput:\n-1 0 3 5 9 12\n9\nOutput: 4"
        ),
        constraints="1 <= n <= 10^4, -10^4 <= nums[i], target <= 10^4",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="-1 0 3 5 9 12\n9", output="4"),
            ProblemExample(input="-1 0 3 5 9 12\n2", output="-1"),
        ],
        test_cases=[
            TestCase(input="-1 0 3 5 9 12\n9", expected_output="4"),
            TestCase(input="-1 0 3 5 9 12\n2", expected_output="-1"),
            TestCase(input="1\n1",              expected_output="0"),
            TestCase(input="1 3 5 7 9\n7",     expected_output="3"),
            TestCase(input="1 3 5 7 9\n6",     expected_output="-1"),
        ],
    ),

    15: Problem(
        id=15, title="Anagram Check", difficulty="Medium", points=20,
        description=(
            "Given two strings on separate lines, print 'true' if the second is an anagram "
            "of the first, 'false' otherwise.\n\n"
            "Example:\nInput:\nanagram\nnagaram\nOutput: true"
        ),
        constraints="1 <= len(s), len(t) <= 5*10^4. Only lowercase letters.",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="anagram\nnagaram", output="true"),
            ProblemExample(input="rat\ncar",         output="false"),
        ],
        test_cases=[
            TestCase(input="anagram\nnagaram", expected_output="true"),
            TestCase(input="rat\ncar",         expected_output="false"),
            TestCase(input="listen\nsilent",   expected_output="true"),
            TestCase(input="hello\nworld",     expected_output="false"),
            TestCase(input="abc\ncba",         expected_output="true"),
        ],
    ),

    # ── HARD ──────────────────────────────────────────────────────────────────

    16: Problem(
        id=16, title="Longest Substring Without Repeating Characters", difficulty="Hard", points=30,
        description=(
            "Given a string, print the length of the longest substring without repeating characters.\n\n"
            "Example:\nInput: abcabcbb\nOutput: 3"
        ),
        constraints="0 <= len(s) <= 5*10^4",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="abcabcbb", output="3"),
            ProblemExample(input="pwwkew",   output="3"),
        ],
        test_cases=[
            TestCase(input="abcabcbb", expected_output="3"),
            TestCase(input="bbbbb",    expected_output="1"),
            TestCase(input="pwwkew",   expected_output="3"),
            TestCase(input="",         expected_output="0"),
            TestCase(input="dvdf",     expected_output="3"),
            TestCase(input="abcdefg",  expected_output="7"),
        ],
    ),

    17: Problem(
        id=17, title="Climbing Stairs", difficulty="Hard", points=30,
        description=(
            "You are climbing n stairs. Each time you can climb 1 or 2 steps. "
            "Print the number of distinct ways to reach the top.\n\n"
            "Example:\nInput: 4\nOutput: 5"
        ),
        constraints="1 <= n <= 45",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="4",  output="5"),
            ProblemExample(input="10", output="89"),
        ],
        test_cases=[
            TestCase(input="1",  expected_output="1"),
            TestCase(input="2",  expected_output="2"),
            TestCase(input="4",  expected_output="5"),
            TestCase(input="10", expected_output="89"),
            TestCase(input="45", expected_output="1836311903"),
        ],
    ),

    18: Problem(
        id=18, title="Merge Intervals", difficulty="Hard", points=35,
        description=(
            "Given n intervals, merge all overlapping ones and print the result.\n\n"
            "Input:\nLine 1: n\nNext n lines: 'start end' per interval\n\n"
            "Output: Each merged interval as 'start end' on its own line.\n\n"
            "Example:\nInput:\n4\n1 3\n2 6\n8 10\n15 18\nOutput:\n1 6\n8 10\n15 18"
        ),
        constraints="1 <= n <= 10^4, 0 <= start <= end <= 10^4",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="4\n1 3\n2 6\n8 10\n15 18", output="1 6\n8 10\n15 18"),
            ProblemExample(input="2\n1 4\n4 5",              output="1 5"),
        ],
        test_cases=[
            TestCase(input="4\n1 3\n2 6\n8 10\n15 18", expected_output="1 6\n8 10\n15 18"),
            TestCase(input="2\n1 4\n4 5",              expected_output="1 5"),
            TestCase(input="3\n1 4\n2 3\n5 7",         expected_output="1 4\n5 7"),
            TestCase(input="3\n1 2\n3 4\n5 6",         expected_output="1 2\n3 4\n5 6"),
        ],
    ),

    19: Problem(
        id=19, title="Longest Common Subsequence", difficulty="Hard", points=35,
        description=(
            "Given two strings on separate lines, print the length of their longest common subsequence.\n\n"
            "A subsequence is a sequence derived by deleting some characters without changing order.\n\n"
            "Example:\nInput:\nabcde\nace\nOutput: 3"
        ),
        constraints="1 <= len(s), len(t) <= 1000. Only lowercase letters.",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(input="abcde\nace",  output="3"),
            ProblemExample(input="abc\nabc",    output="3"),
            ProblemExample(input="abc\ndef",    output="0"),
        ],
        test_cases=[
            TestCase(input="abcde\nace",    expected_output="3"),
            TestCase(input="abc\nabc",      expected_output="3"),
            TestCase(input="abc\ndef",      expected_output="0"),
            TestCase(input="oxcpqrsvwf\nshmtulqrypy", expected_output="2"),
            TestCase(input="bsbininm\njmjkbkjkv",     expected_output="1"),
        ],
    ),

    20: Problem(
        id=20, title="Word Frequency", difficulty="Hard", points=30,
        description=(
            "Given a sentence, print each unique word and its frequency, "
            "sorted alphabetically, one per line as 'word count'.\n\n"
            "Input: A single line of space-separated words (lowercase).\n\n"
            "Example:\nInput: the cat sat on the mat the cat\n"
            "Output:\ncat 2\nmat 1\non 1\nsat 1\nthe 3"
        ),
        constraints="1 <= words <= 10^4. Only lowercase letters and spaces.",
        time_limit_seconds=5, memory_limit_mb=256,
        examples=[
            ProblemExample(
                input="the cat sat on the mat the cat",
                output="cat 2\nmat 1\non 1\nsat 1\nthe 3"
            ),
        ],
        test_cases=[
            TestCase(
                input="the cat sat on the mat the cat",
                expected_output="cat 2\nmat 1\non 1\nsat 1\nthe 3"
            ),
            TestCase(
                input="hello world hello",
                expected_output="hello 2\nworld 1"
            ),
            TestCase(
                input="a b c a b a",
                expected_output="a 3\nb 2\nc 1"
            ),
            TestCase(
                input="one",
                expected_output="one 1"
            ),
        ],
    ),
}

# ============= JUDGE0 INTERACTION =============

async def get_judge0_status() -> bool:
    """Check if Judge0 is running and healthy"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Judge0 v1.13 health endpoint
            response = await client.get(f"{JUDGE0_URL}/system_info")
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Judge0 health check failed: {e}")
        return False


async def submit_to_judge0(code: str, language_id: int, stdin: str, expected_output: str) -> Dict[str, Any]:
    """
    Submit code to Judge0 for evaluation asynchronously.
    Returns token for polling results.
    """
    headers = {"Content-Type": "application/json"}
    if JUDGE0_API_KEY:
        headers["X-Auth-Token"] = JUDGE0_API_KEY

    # Java JVM needs virtual memory for heap reservation — disable isolate memory limit for JVM languages
    # (JVM languages have high memory utilization, currently skipped)

    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": stdin,
        "expected_output": expected_output,
        # Both MUST be true on WSL2 — otherwise isolate uses --cg which fails
        "enable_per_process_and_thread_time_limit": True,
        "enable_per_process_and_thread_memory_limit": True,
        "cpu_time_limit": 10,
        "wall_time_limit": 15,
        # Java needs high virtual memory limit so JVM can reserve heap
        # Other languages use 512000 KB
        "memory_limit": 512000,
        "max_processes_and_or_threads": 120,
    }

    try:
        logger.info(f"🔍 Submitting to Judge0 (async): language_id={language_id}, stdin_len={len(stdin)}, code_len={len(code)}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{JUDGE0_URL}/submissions",
                json=payload,
                headers=headers,
            )
            logger.info(f"📨 Judge0 Response Status: {response.status_code}")
            
            if response.status_code not in [200, 201]:
                logger.error(f"📨 Judge0 Error Response: {response.status_code} - {response.text}")
                # Try to parse error details
                try:
                    error_detail = response.json()
                    logger.error(f"📨 Judge0 Error Details: {error_detail}")
                except:
                    pass
                # For 500 errors from Judge0 (often Redis-related), retry or fail gracefully
                if response.status_code == 500:
                    raise HTTPException(status_code=503, detail="Judge0 service temporarily unavailable (500 error)")
                raise HTTPException(status_code=response.status_code, detail="Judge0 submission failed")
            
            data = response.json()
            token = data.get("token")
            logger.info(f"✅ Got token from Judge0: {token}")
            return data
            
    except httpx.TimeoutException:
        logger.error(f"❌ Judge0 request timeout after 15 seconds")
        raise HTTPException(status_code=504, detail="Judge0 request timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error submitting to Judge0: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to submit to Judge0: {str(e)}")


async def poll_judge0_result(token: str, max_retries: int = 30) -> Dict[str, Any]:
    """Poll Judge0 for submission result with exponential backoff"""
    headers = {}
    if JUDGE0_API_KEY:
        headers["X-Auth-Token"] = JUDGE0_API_KEY

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{JUDGE0_URL}/submissions/{token}",
                    headers=headers,
                    params={"base64": "false"}
                )
                
                if response.status_code not in [200, 202]:
                    logger.warning(f"Judge0 poll returned status {response.status_code}")
                    if response.status_code >= 500:
                        raise HTTPException(status_code=500, detail="Judge0 polling service error")
                    continue
                
                data = response.json()
                
                # Status codes: 1=In Queue, 2=Processing, 3=Accepted, 4=Wrong Answer, etc.
                status_id = data.get("status", {}).get("id", 0) if data.get("status") else 0
                
                # Check if execution is complete (any status except 1=queue, 2=processing)
                if status_id not in [1, 2]:
                    logger.info(f"✅ Judge0 result ready: token={token}, status={status_id}")
                    return data

                # Not done yet, wait before retrying
                sleep_time = min(1.0 * (2 ** attempt), 10.0)  # Exponential: 1s, 2s, 4s, 8s, cap 10s
                await asyncio.sleep(sleep_time)

        except httpx.TimeoutException:
            logger.warning(f"Judge0 poll timeout on attempt {attempt+1}/{max_retries}")
            continue
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Error polling Judge0 (attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"Judge0 polling failed: {str(e)}")

    raise HTTPException(status_code=504, detail="Judge0 result polling timed out after 30 attempts")


def map_judge0_verdict(judge0_status_id: int, passed_count: int, total_count: int) -> VerdictEnum:
    """Map Judge0 status code to submission verdict"""
    # Status codes: 1=In Queue, 2=Processing, 3=Accepted, 4=Wrong Answer, 5=Time Limit, etc.
    judge0_verdicts = {
        1: VerdictEnum.PENDING,
        2: VerdictEnum.PENDING,
        3: VerdictEnum.ACCEPTED if passed_count == total_count else VerdictEnum.WRONG_ANSWER,
        4: VerdictEnum.WRONG_ANSWER,
        5: VerdictEnum.TIME_LIMIT,
        6: VerdictEnum.COMPILATION_ERROR,
        7: VerdictEnum.RUNTIME_ERROR,
        8: VerdictEnum.RUNTIME_ERROR,
        9: VerdictEnum.TIME_LIMIT,
        10: VerdictEnum.RUNTIME_ERROR,
        11: VerdictEnum.RUNTIME_ERROR,
        12: VerdictEnum.COMPILATION_ERROR,
        13: VerdictEnum.RUNTIME_ERROR,
        14: VerdictEnum.RUNTIME_ERROR,
    }
    return judge0_verdicts.get(judge0_status_id, VerdictEnum.RUNTIME_ERROR)


async def normalize_output(output: str) -> str:
    """Normalize output for comparison (CRLF-aware, per-line trailing whitespace stripped)"""
    if not output:
        return ""
    text = output.replace('\r\n', '\n').replace('\r', '\n')
    lines = [line.rstrip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


# ============= SCORING ENGINE =============

# First-solve tracker  {problem_id: solve_count}
_first_solve_counts: Dict[int, int] = {}

def calculate_score(
    problem: "Problem",
    passed: int,
    total: int,
    avg_runtime_ms: Optional[float],
    avg_memory_mb: Optional[float],
    prior_wrong_attempts: int = 0,
    streak_days: int = 0,
) -> ScoreBreakdown:
    """
    VISIBLE score (shown to user, out of 10):
      Correctness  = (passed/total) × 7.0          max 7.0
      Time bonus   = 1.5 / 1.0 / 0.5 / 0.0         max 1.5
      Memory bonus = 1.5 / 1.0 / 0.5 / 0.0         max 1.5
      Total capped at 10.0

    HIDDEN score (leaderboard only):
      = visible_score
      + first_solve_bonus  (+15 for first 5 solvers)
      + streak_bonus       (+5 per day, max +25)
      − wrong_penalty      (−2 per WA before AC)
    """
    if total == 0:
        return ScoreBreakdown(
            correctness=0, time_bonus=0, memory_bonus=0,
            visible_score=0, first_solve_bonus=0,
            streak_bonus=0, wrong_attempt_penalty=0, leaderboard_points=0
        )

    # ── Correctness (0–7.0) ─────────────────────────────────────────────────
    correctness = round((passed / total) * 7.0, 1)

    # ── Time bonus (0–1.5) ──────────────────────────────────────────────────
    time_bonus = 0.0
    if avg_runtime_ms is not None and problem.time_limit_seconds > 0:
        ratio = avg_runtime_ms / (problem.time_limit_seconds * 1000)
        if   ratio <= 0.30: time_bonus = 1.5
        elif ratio <= 0.60: time_bonus = 1.0
        elif ratio <= 0.90: time_bonus = 0.5

    # ── Memory bonus (0–1.5) ────────────────────────────────────────────────
    memory_bonus = 0.0
    if avg_memory_mb is not None and problem.memory_limit_mb > 0:
        ratio = avg_memory_mb / problem.memory_limit_mb
        if   ratio <= 0.30: memory_bonus = 1.5
        elif ratio <= 0.60: memory_bonus = 1.0
        elif ratio <= 0.90: memory_bonus = 0.5

    visible_score = min(10.0, round(correctness + time_bonus + memory_bonus, 1))

    # ── Hidden: first-solve bonus (+15) ─────────────────────────────────────
    first_solve_bonus = 0.0
    if passed == total:
        count = _first_solve_counts.get(problem.id, 0)
        if count < 5:
            first_solve_bonus = 15.0
            _first_solve_counts[problem.id] = count + 1

    # ── Hidden: streak bonus (+5/day, max +25) ──────────────────────────────
    streak_bonus = min(25.0, streak_days * 5.0)

    # ── Hidden: wrong-attempt penalty (−2 each) ─────────────────────────────
    wrong_penalty = prior_wrong_attempts * 2.0

    leaderboard_points = max(0.0, round(
        visible_score + first_solve_bonus + streak_bonus - wrong_penalty, 1
    ))

    return ScoreBreakdown(
        correctness=correctness,
        time_bonus=time_bonus,
        memory_bonus=memory_bonus,
        visible_score=visible_score,
        first_solve_bonus=first_solve_bonus,
        streak_bonus=streak_bonus,
        wrong_attempt_penalty=wrong_penalty,
        leaderboard_points=leaderboard_points,
    )


async def evaluate_submission(
    code: str,
    language: str,
    test_cases: List[TestCase],
    problem_id: int,
    prior_wrong_attempts: int = 0,
    streak_days: int = 0,
) -> tuple[List[TestCaseResult], VerdictEnum, ScoreBreakdown]:
    """
    Evaluate submission against all test cases using Judge0.
    Returns (test_results, overall_verdict, score_breakdown)
    """
    test_results = []
    passed_count = 0
    runtimes: List[float] = []
    memories: List[float] = []

    if language.lower() not in LANGUAGE_IDS:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

    language_id = LANGUAGE_IDS[language.lower()]

    try:
        is_healthy = await get_judge0_status()
        if not is_healthy:
            logger.warning("Judge0 health check failed, but will attempt submission anyway")
    except Exception as e:
        logger.warning(f"Judge0 health check raised exception: {e}, continuing with submission")

    for idx, test_case in enumerate(test_cases, 1):
        try:
            judge0_response = await submit_to_judge0(
                code=code,
                language_id=language_id,
                stdin=test_case.input,
                expected_output=test_case.expected_output
            )

            token = judge0_response.get("token")
            if not token:
                raise ValueError("Judge0 returned no token")

            result = await poll_judge0_result(token)

            actual_output = result.get("stdout", "").strip() if result.get("stdout") else ""
            stderr = result.get("stderr", "").strip() if result.get("stderr") else ""
            compile_output = result.get("compile_output", "").strip() if result.get("compile_output") else ""
            status_id = result.get("status", {}).get("id", 0) if result.get("status") else 0

            rt = float(result.get("time")) if result.get("time") else None
            mem = float(result.get("memory")) if result.get("memory") else None
            if rt:  runtimes.append(rt * 1000)   # convert s → ms
            if mem: memories.append(mem / 1024)  # convert KB → MB

            if compile_output and status_id in [11, 12, 13, 14, 15]:
                passed = False
                error_msg = compile_output
            elif status_id in [5, 6]:
                passed = False
                error_msg = stderr if stderr else "Runtime error"
            else:
                match, _ = OutputNormalizer.compare(
                    actual_output, test_case.expected_output, normalize_mode="lines"
                )
                passed = match and (status_id == 3)
                error_msg = stderr if stderr else None

            if passed:
                passed_count += 1

            test_results.append(TestCaseResult(
                test_case_number=idx,
                input=test_case.input[:100],
                expected_output=(await normalize_output(test_case.expected_output))[:100],
                actual_output=(await normalize_output(actual_output))[:100],
                passed=passed,
                runtime_ms=rt * 1000 if rt else None,
                memory_mb=mem / 1024 if mem else None,
                error=error_msg
            ))

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error evaluating test case {idx}: {type(e).__name__}: {e}")
            test_results.append(TestCaseResult(
                test_case_number=idx,
                input=test_case.input[:100],
                expected_output=test_case.expected_output[:100],
                actual_output="",
                passed=False,
                error=str(e)
            ))

    # Verdict
    if passed_count == len(test_cases):
        verdict = VerdictEnum.ACCEPTED
    elif passed_count > 0:
        verdict = VerdictEnum.PARTIAL
    else:
        verdict = VerdictEnum.WRONG_ANSWER

    avg_rt  = sum(runtimes) / len(runtimes)   if runtimes  else None
    avg_mem = sum(memories) / len(memories)   if memories  else None

    problem = PROBLEMS.get(problem_id)
    if problem:
        breakdown = calculate_score(
            problem=problem,
            passed=passed_count,
            total=len(test_cases),
            avg_runtime_ms=avg_rt,
            avg_memory_mb=avg_mem,
            prior_wrong_attempts=prior_wrong_attempts,
            streak_days=streak_days,
        )
    else:
        # Fallback if problem not found
        ratio = passed_count / len(test_cases) if test_cases else 0
        pts = round(100 * ratio)
        breakdown = ScoreBreakdown(
            base_points=pts, time_bonus=0, memory_bonus=0,
            streak_bonus=0, first_solve_bonus=0,
            wrong_attempt_penalty=0, total_points=pts, multiplier=1.0
        )

    return test_results, verdict, breakdown


# ============= BACKGROUND TASKS =============

async def update_leaderboard(
    user_id: str,
    username: str,
    house: str,
    problem_id: int,
    score: int,
    language: str
):
    """Send leaderboard update to Leaderboard Service"""
    try:
        payload = {
            "user_id": user_id,
            "username": username,
            "house": house,
            "problem_id": problem_id,
            "points": score,
            "language": language,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{LEADERBOARD_URL}/api/v1/update_score",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Leaderboard updated for {username}: +{score} points")
            else:
                logger.error(f"Leaderboard update failed: {response.text}")

    except Exception as e:
        logger.error(f"Error updating leaderboard: {e}")


# ============= API ENDPOINTS =============

@app.get("/health")
async def health_check():
    """Service health check"""
    judge0_healthy = await get_judge0_status()
    return {
        "status": "healthy" if judge0_healthy else "degraded",
        "judge0": "connected" if judge0_healthy else "offline",
        "service": "judge",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/problems", response_model=Dict[str, Any])
async def get_problems(limit: int = 100, offset: int = 0):
    """Get all problems with pagination"""
    try:
        all_problems = list(PROBLEMS.values())
        paginated = all_problems[offset:offset + limit]

        return {
            "status": "success",
            "total": len(all_problems),
            "returned": len(paginated),
            "problems": paginated
        }
    except Exception as e:
        logger.error(f"Error fetching problems: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/problems/{problem_id}", response_model=Dict[str, Any])
async def get_problem(problem_id: int):
    """Get specific problem details"""
    try:
        if problem_id not in PROBLEMS:
            raise HTTPException(status_code=404, detail=f"Problem {problem_id} not found")

        problem = PROBLEMS[problem_id]
        return {
            "status": "success",
            "problem": problem
        }
    except Exception as e:
        logger.error(f"Error fetching problem {problem_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/submissions", response_model=Dict[str, Any])
async def submit_code(request: SubmissionRequest, background_tasks: BackgroundTasks):
    """Submit code for evaluation"""
    try:
        # Validate problem exists
        if request.problem_id not in PROBLEMS:
            raise HTTPException(status_code=404, detail=f"Problem {request.problem_id} not found")

        problem = PROBLEMS[request.problem_id]
        logger.info(f"📝 Processing submission for problem {request.problem_id} in {request.language}")

        # Evaluate submission
        test_results, verdict, breakdown = await evaluate_submission(
            code=request.code,
            language=request.language,
            test_cases=problem.test_cases,
            problem_id=request.problem_id,
            prior_wrong_attempts=request.prior_wrong_attempts,
            streak_days=request.streak_days,
        )

        final_score = breakdown.visible_score

        # Persist to PostgreSQL
        db_id = await DatabaseService.save_submission(
            user_id=request.user_id,
            problem_id=request.problem_id,
            language=request.language,
            source_code=request.code,
            verdict=verdict.value,
            score=final_score,
            passed_tests=sum(1 for r in test_results if r.passed),
            total_tests=len(test_results),
            execution_time=0.0,
        )

        avg_rt  = sum(r.runtime_ms for r in test_results if r.runtime_ms) / max(1, sum(1 for r in test_results if r.runtime_ms)) if any(r.runtime_ms for r in test_results) else None
        avg_mem = sum(r.memory_mb for r in test_results if r.memory_mb) / max(1, sum(1 for r in test_results if r.memory_mb)) if any(r.memory_mb for r in test_results) else None

        submission_result = SubmissionResult(
            submission_id=str(db_id),
            verdict=verdict,
            total_test_cases=len(test_results),
            passed_test_cases=sum(1 for r in test_results if r.passed),
            language=request.language,
            runtime_ms=avg_rt,
            memory_mb=avg_mem,
            test_cases=test_results,
            score=final_score,
            score_breakdown=breakdown,
            submitted_code=request.code,
            submission_time=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Submission {db_id} completed with verdict: {verdict}")

        if verdict in (VerdictEnum.ACCEPTED, VerdictEnum.PARTIAL):
            background_tasks.add_task(
                update_leaderboard,
                user_id=request.user_id,
                username=request.username,
                house=request.house,
                problem_id=request.problem_id,
                score=breakdown.leaderboard_points,
                language=request.language
            )
            logger.info(f"🏆 Leaderboard update queued for {request.username}: visible={final_score}/10, leaderboard={breakdown.leaderboard_points}")

        return {
            "status": "success",
            "submission": submission_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error evaluating submission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Submission evaluation failed: {str(e)}")


@app.post("/api/v1/submissions/run", response_model=Dict[str, Any])
async def run_submission(request: RunSubmissionRequest):
    """Run code on custom test cases"""
    try:
        if request.problem_id not in PROBLEMS:
            raise HTTPException(status_code=404, detail=f"Problem {request.problem_id} not found")

        problem = PROBLEMS[request.problem_id]

        # Use provided test cases or problem's test cases
        test_cases = request.test_cases or problem.test_cases

        # Convert dict test cases to TestCase objects if needed
        if test_cases and isinstance(test_cases[0], dict):
            test_cases = [
                TestCase(input=tc["input"], expected_output=tc["expected_output"])
                for tc in test_cases
            ]

        test_results, verdict, score = await evaluate_submission(
            code=request.code,
            language=request.language,
            test_cases=test_cases,
            problem_id=request.problem_id
        )

        return {
            "status": "success",
            "verdict": verdict,
            "passed": sum(1 for r in test_results if r.passed),
            "total": len(test_results),
            "test_cases": test_results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running submission: {e}")
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")


@app.get("/api/v1/submissions/{submission_id}", response_model=Dict[str, Any])
async def get_submission(submission_id: str):
    """Get submission details"""
    try:
        try:
            db_submission_id = int(submission_id)
        except (ValueError, TypeError):
            return {
                "status": "pending",
                "submission": {
                    "submission_id": submission_id,
                    "verdict": "Pending",
                    "status": "pending"
                }
            }

        submission_data = await DatabaseService.get_submission(db_submission_id)

        if submission_data is None:
            return {
                "status": "pending",
                "submission": {
                    "submission_id": submission_id,
                    "verdict": "Pending",
                    "status": "pending"
                }
            }

        logger.info(f"🔍 Retrieved submission {submission_id}")

        return {
            "status": "success",
            "submission": SubmissionResult(
                submission_id=str(submission_data["id"]),
                verdict=submission_data["verdict"],
                total_test_cases=submission_data["total_tests"],
                passed_test_cases=submission_data["passed_tests"],
                language=submission_data["language"],
                test_cases=[],
                score=submission_data["score"],
                submitted_code="[code hidden]",
                submission_time=submission_data["created_at"].isoformat() if submission_data.get("created_at") else datetime.now().isoformat()
            )
        }
    except Exception as e:
        logger.error(f"❌ Error fetching submission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve submission: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
