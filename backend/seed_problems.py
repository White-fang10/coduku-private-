"""
seed_problems.py — Seeds MongoDB with 20 problems (Easy / Medium / Hard).
Run: python seed_problems.py
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/coding_platform")
client = MongoClient(MONGO_URI)
db = client["coding_platform"]
col = db["questions"]

PROBLEMS = [
    # ── EASY ──────────────────────────────────────────────────────────────────
    {
        "title": "Hello World", "difficulty": "Easy", "time_limit": 5, "memory_limit": 256,
        "description": "Print the text: Hello, World!\n\nNo input is given.\n\nOutput: Hello, World!",
        "constraints": "No input.",
        "test_cases": [{"input": [], "output": "Hello, World!", "function_name": "solution"}],
        "solution": "def solution(): return 'Hello, World!'",
    },
    {
        "title": "Sum of Two Numbers", "difficulty": "Easy", "time_limit": 5, "memory_limit": 256,
        "description": "Read two integers (space-separated) and print their sum.\n\nExample:\nInput: 3 5\nOutput: 8",
        "constraints": "-10^9 <= a, b <= 10^9",
        "test_cases": [
            {"input": [3, 5],     "output": "8",    "function_name": "solution"},
            {"input": [-1, 1],    "output": "0",    "function_name": "solution"},
            {"input": [0, 0],     "output": "0",    "function_name": "solution"},
            {"input": [100, 200], "output": "300",  "function_name": "solution"},
            {"input": [-50, -50], "output": "-100", "function_name": "solution"},
        ],
        "solution": "def solution(a, b): return a + b",
    },
    {
        "title": "Reverse a String", "difficulty": "Easy", "time_limit": 5, "memory_limit": 256,
        "description": "Read a string and print it reversed.\n\nExample:\nInput: hello\nOutput: olleh",
        "constraints": "1 <= len(s) <= 10^5",
        "test_cases": [
            {"input": "hello",   "output": "olleh",   "function_name": "solution"},
            {"input": "abcde",   "output": "edcba",   "function_name": "solution"},
            {"input": "a",       "output": "a",       "function_name": "solution"},
            {"input": "racecar", "output": "racecar", "function_name": "solution"},
            {"input": "Python",  "output": "nohtyP",  "function_name": "solution"},
        ],
        "solution": "def solution(s): return s[::-1]",
    },
    {
        "title": "Even or Odd", "difficulty": "Easy", "time_limit": 5, "memory_limit": 256,
        "description": "Given an integer n, print 'Even' if even, 'Odd' otherwise.\n\nExample:\nInput: 4\nOutput: Even",
        "constraints": "-10^9 <= n <= 10^9",
        "test_cases": [
            {"input": 4,  "output": "Even", "function_name": "solution"},
            {"input": 7,  "output": "Odd",  "function_name": "solution"},
            {"input": 0,  "output": "Even", "function_name": "solution"},
            {"input": -5, "output": "Odd",  "function_name": "solution"},
            {"input": -2, "output": "Even", "function_name": "solution"},
        ],
        "solution": "def solution(n): return 'Even' if n % 2 == 0 else 'Odd'",
    },
    {
        "title": "Count Vowels", "difficulty": "Easy", "time_limit": 5, "memory_limit": 256,
        "description": "Count vowels (a,e,i,o,u, case-insensitive) in a string.\n\nExample:\nInput: Hello World\nOutput: 3",
        "constraints": "1 <= len(s) <= 10^5",
        "test_cases": [
            {"input": "Hello World", "output": "3", "function_name": "solution"},
            {"input": "aeiou",       "output": "5", "function_name": "solution"},
            {"input": "rhythm",      "output": "0", "function_name": "solution"},
            {"input": "Programming", "output": "3", "function_name": "solution"},
            {"input": "AEIOU",       "output": "5", "function_name": "solution"},
        ],
        "solution": "def solution(s): return sum(1 for c in s.lower() if c in 'aeiou')",
    },
    {
        "title": "FizzBuzz", "difficulty": "Easy", "time_limit": 5, "memory_limit": 256,
        "description": (
            "Print numbers 1 to n. Multiples of 3: Fizz. Multiples of 5: Buzz. Both: FizzBuzz.\n\n"
            "Example:\nInput: 5\nOutput:\n1\n2\nFizz\n4\nBuzz"
        ),
        "constraints": "1 <= n <= 10^4",
        "test_cases": [
            {"input": 1,  "output": "1",                                                                                                    "function_name": "solution"},
            {"input": 3,  "output": "1\n2\nFizz",                                                                                          "function_name": "solution"},
            {"input": 5,  "output": "1\n2\nFizz\n4\nBuzz",                                                                                 "function_name": "solution"},
            {"input": 15, "output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz",                           "function_name": "solution"},
        ],
        "solution": (
            "def solution(n):\n"
            "    return '\\n'.join('FizzBuzz' if i%15==0 else 'Fizz' if i%3==0 else 'Buzz' if i%5==0 else str(i) for i in range(1,n+1))"
        ),
    },
    {
        "title": "Fibonacci Number", "difficulty": "Easy", "time_limit": 5, "memory_limit": 256,
        "description": "Given n, print the nth Fibonacci number. F(0)=0, F(1)=1.\n\nExample:\nInput: 6\nOutput: 8",
        "constraints": "0 <= n <= 30",
        "test_cases": [
            {"input": 0,  "output": "0",    "function_name": "solution"},
            {"input": 1,  "output": "1",    "function_name": "solution"},
            {"input": 6,  "output": "8",    "function_name": "solution"},
            {"input": 10, "output": "55",   "function_name": "solution"},
            {"input": 20, "output": "6765", "function_name": "solution"},
        ],
        "solution": "def solution(n):\n    a,b=0,1\n    for _ in range(n): a,b=b,a+b\n    return a",
    },
    {
        "title": "Palindrome Check", "difficulty": "Easy", "time_limit": 5, "memory_limit": 256,
        "description": "Print 'true' if the string is a palindrome (ignore spaces/case), 'false' otherwise.\n\nExample:\nInput: racecar\nOutput: true",
        "constraints": "1 <= len(s) <= 10^5",
        "test_cases": [
            {"input": "racecar",                     "output": "true",  "function_name": "solution"},
            {"input": "hello",                       "output": "false", "function_name": "solution"},
            {"input": "A man a plan a canal Panama", "output": "true",  "function_name": "solution"},
            {"input": "Was it a car or a cat I saw", "output": "true",  "function_name": "solution"},
            {"input": "python",                      "output": "false", "function_name": "solution"},
        ],
        "solution": "def solution(s):\n    s=s.replace(' ','').lower()\n    return 'true' if s==s[::-1] else 'false'",
    },

    # ── MEDIUM ────────────────────────────────────────────────────────────────
    {
        "title": "Two Sum", "difficulty": "Medium", "time_limit": 5, "memory_limit": 256,
        "description": (
            "Given an array and a target, print the 0-based indices of two numbers that sum to target.\n\n"
            "Input:\nLine 1: space-separated integers\nLine 2: target\n\nExample:\nInput:\n2 7 11 15\n9\nOutput: 0 1"
        ),
        "constraints": "2 <= n <= 10^4",
        "test_cases": [
            {"input": [[2,7,11,15], 9],  "output": "0 1", "function_name": "solution"},
            {"input": [[3,2,4], 6],      "output": "1 2", "function_name": "solution"},
            {"input": [[3,3], 6],        "output": "0 1", "function_name": "solution"},
            {"input": [[1,5,3,7], 8],    "output": "1 2", "function_name": "solution"},
            {"input": [[2,5,5,11], 10],  "output": "1 2", "function_name": "solution"},
        ],
        "solution": "def solution(nums, target):\n    seen={}\n    for i,n in enumerate(nums):\n        if target-n in seen: return f'{seen[target-n]} {i}'\n        seen[n]=i",
    },
    {
        "title": "Valid Parentheses", "difficulty": "Medium", "time_limit": 5, "memory_limit": 256,
        "description": "Given a bracket string, print 'true' if valid, 'false' otherwise.\n\nExample:\nInput: ()[]{}\nOutput: true",
        "constraints": "1 <= len(s) <= 10^4",
        "test_cases": [
            {"input": "()[]{}",  "output": "true",  "function_name": "solution"},
            {"input": "(]",      "output": "false", "function_name": "solution"},
            {"input": "([)]",    "output": "false", "function_name": "solution"},
            {"input": "{[]}",    "output": "true",  "function_name": "solution"},
            {"input": "((((",    "output": "false", "function_name": "solution"},
        ],
        "solution": "def solution(s):\n    stack,m=[],{')':'(', ']':'[', '}':'{'}\n    for c in s:\n        if c in m:\n            if not stack or stack[-1]!=m[c]: return 'false'\n            stack.pop()\n        else: stack.append(c)\n    return 'true' if not stack else 'false'",
    },
    {
        "title": "Factorial", "difficulty": "Medium", "time_limit": 5, "memory_limit": 256,
        "description": "Given n, print n! (factorial).\n\nExample:\nInput: 5\nOutput: 120",
        "constraints": "0 <= n <= 12",
        "test_cases": [
            {"input": 0,  "output": "1",         "function_name": "solution"},
            {"input": 1,  "output": "1",         "function_name": "solution"},
            {"input": 5,  "output": "120",       "function_name": "solution"},
            {"input": 10, "output": "3628800",   "function_name": "solution"},
            {"input": 12, "output": "479001600", "function_name": "solution"},
        ],
        "solution": "def solution(n):\n    r=1\n    for i in range(2,n+1): r*=i\n    return r",
    },
    {
        "title": "Prime Check", "difficulty": "Medium", "time_limit": 5, "memory_limit": 256,
        "description": "Print 'Prime' if n is prime, 'Not Prime' otherwise.\n\nExample:\nInput: 17\nOutput: Prime",
        "constraints": "2 <= n <= 10^6",
        "test_cases": [
            {"input": 2,   "output": "Prime",     "function_name": "solution"},
            {"input": 17,  "output": "Prime",     "function_name": "solution"},
            {"input": 4,   "output": "Not Prime", "function_name": "solution"},
            {"input": 97,  "output": "Prime",     "function_name": "solution"},
            {"input": 100, "output": "Not Prime", "function_name": "solution"},
        ],
        "solution": "def solution(n):\n    if n<2: return 'Not Prime'\n    for i in range(2,int(n**0.5)+1):\n        if n%i==0: return 'Not Prime'\n    return 'Prime'",
    },
    {
        "title": "Maximum Subarray", "difficulty": "Medium", "time_limit": 5, "memory_limit": 256,
        "description": "Given space-separated integers, print the maximum subarray sum.\n\nExample:\nInput: -2 1 -3 4 -1 2 1 -5 4\nOutput: 6",
        "constraints": "1 <= n <= 10^5",
        "test_cases": [
            {"input": [-2,1,-3,4,-1,2,1,-5,4], "output": "6",  "function_name": "solution"},
            {"input": [1],                      "output": "1",  "function_name": "solution"},
            {"input": [5,4,-1,7,8],             "output": "23", "function_name": "solution"},
            {"input": [-1,-2,-3],               "output": "-1", "function_name": "solution"},
            {"input": [2,-1,2,3,4,-5],          "output": "10", "function_name": "solution"},
        ],
        "solution": "def solution(*nums):\n    best=cur=nums[0]\n    for n in nums[1:]:\n        cur=max(n,cur+n); best=max(best,cur)\n    return best",
    },
    {
        "title": "Binary Search", "difficulty": "Medium", "time_limit": 5, "memory_limit": 256,
        "description": "Given a sorted array and a target, print the 0-based index or -1 if not found.\n\nInput:\nLine 1: sorted integers\nLine 2: target\n\nExample:\nInput:\n-1 0 3 5 9 12\n9\nOutput: 4",
        "constraints": "1 <= n <= 10^4",
        "test_cases": [
            {"input": [[-1,0,3,5,9,12], 9], "output": "4",  "function_name": "solution"},
            {"input": [[-1,0,3,5,9,12], 2], "output": "-1", "function_name": "solution"},
            {"input": [[1], 1],             "output": "0",  "function_name": "solution"},
            {"input": [[1,3,5,7,9], 7],     "output": "3",  "function_name": "solution"},
            {"input": [[1,3,5,7,9], 6],     "output": "-1", "function_name": "solution"},
        ],
        "solution": "def solution(nums, target):\n    lo,hi=0,len(nums)-1\n    while lo<=hi:\n        mid=(lo+hi)//2\n        if nums[mid]==target: return mid\n        elif nums[mid]<target: lo=mid+1\n        else: hi=mid-1\n    return -1",
    },
    {
        "title": "Anagram Check", "difficulty": "Medium", "time_limit": 5, "memory_limit": 256,
        "description": "Given two strings on separate lines, print 'true' if one is an anagram of the other.\n\nExample:\nInput:\nanagram\nnagaram\nOutput: true",
        "constraints": "1 <= len(s) <= 5*10^4",
        "test_cases": [
            {"input": ["anagram", "nagaram"], "output": "true",  "function_name": "solution"},
            {"input": ["rat", "car"],         "output": "false", "function_name": "solution"},
            {"input": ["listen", "silent"],   "output": "true",  "function_name": "solution"},
            {"input": ["hello", "world"],     "output": "false", "function_name": "solution"},
            {"input": ["abc", "cba"],         "output": "true",  "function_name": "solution"},
        ],
        "solution": "def solution(s,t):\n    from collections import Counter\n    return 'true' if Counter(s)==Counter(t) else 'false'",
    },

    # ── HARD ──────────────────────────────────────────────────────────────────
    {
        "title": "Longest Substring Without Repeating Characters", "difficulty": "Hard", "time_limit": 5, "memory_limit": 256,
        "description": "Print the length of the longest substring without repeating characters.\n\nExample:\nInput: abcabcbb\nOutput: 3",
        "constraints": "0 <= len(s) <= 5*10^4",
        "test_cases": [
            {"input": "abcabcbb", "output": "3", "function_name": "solution"},
            {"input": "bbbbb",    "output": "1", "function_name": "solution"},
            {"input": "pwwkew",   "output": "3", "function_name": "solution"},
            {"input": "",         "output": "0", "function_name": "solution"},
            {"input": "dvdf",     "output": "3", "function_name": "solution"},
            {"input": "abcdefg",  "output": "7", "function_name": "solution"},
        ],
        "solution": "def solution(s):\n    seen,start,best={},0,0\n    for i,c in enumerate(s):\n        if c in seen and seen[c]>=start: start=seen[c]+1\n        seen[c]=i; best=max(best,i-start+1)\n    return best",
    },
    {
        "title": "Climbing Stairs", "difficulty": "Hard", "time_limit": 5, "memory_limit": 256,
        "description": "You can climb 1 or 2 steps at a time. Print the number of distinct ways to reach the top of n stairs.\n\nExample:\nInput: 4\nOutput: 5",
        "constraints": "1 <= n <= 45",
        "test_cases": [
            {"input": 1,  "output": "1",          "function_name": "solution"},
            {"input": 2,  "output": "2",          "function_name": "solution"},
            {"input": 4,  "output": "5",          "function_name": "solution"},
            {"input": 10, "output": "89",         "function_name": "solution"},
            {"input": 45, "output": "1836311903", "function_name": "solution"},
        ],
        "solution": "def solution(n):\n    a,b=1,1\n    for _ in range(n-1): a,b=b,a+b\n    return b",
    },
    {
        "title": "Merge Intervals", "difficulty": "Hard", "time_limit": 5, "memory_limit": 256,
        "description": "Merge overlapping intervals.\n\nInput:\nLine 1: n\nNext n lines: 'start end'\n\nOutput: Each merged interval as 'start end'.\n\nExample:\nInput:\n4\n1 3\n2 6\n8 10\n15 18\nOutput:\n1 6\n8 10\n15 18",
        "constraints": "1 <= n <= 10^4",
        "test_cases": [
            {"input": [[1,3],[2,6],[8,10],[15,18]], "output": "1 6\n8 10\n15 18", "function_name": "solution"},
            {"input": [[1,4],[4,5]],                "output": "1 5",             "function_name": "solution"},
            {"input": [[1,4],[2,3],[5,7]],          "output": "1 4\n5 7",        "function_name": "solution"},
            {"input": [[1,2],[3,4],[5,6]],          "output": "1 2\n3 4\n5 6",   "function_name": "solution"},
        ],
        "solution": "def solution(*ivs):\n    ivs=sorted(ivs,key=lambda x:x[0]); m=[list(ivs[0])]\n    for s,e in ivs[1:]:\n        if s<=m[-1][1]: m[-1][1]=max(m[-1][1],e)\n        else: m.append([s,e])\n    return '\\n'.join(f'{s} {e}' for s,e in m)",
    },
    {
        "title": "Longest Common Subsequence", "difficulty": "Hard", "time_limit": 5, "memory_limit": 256,
        "description": "Given two strings on separate lines, print the length of their longest common subsequence.\n\nExample:\nInput:\nabcde\nace\nOutput: 3",
        "constraints": "1 <= len(s), len(t) <= 1000",
        "test_cases": [
            {"input": ["abcde", "ace"],          "output": "3", "function_name": "solution"},
            {"input": ["abc", "abc"],            "output": "3", "function_name": "solution"},
            {"input": ["abc", "def"],            "output": "0", "function_name": "solution"},
            {"input": ["oxcpqrsvwf","shmtulqrypy"], "output": "2", "function_name": "solution"},
        ],
        "solution": "def solution(s,t):\n    m,n=len(s),len(t); dp=[[0]*(n+1) for _ in range(m+1)]\n    for i in range(1,m+1):\n        for j in range(1,n+1):\n            dp[i][j]=dp[i-1][j-1]+1 if s[i-1]==t[j-1] else max(dp[i-1][j],dp[i][j-1])\n    return dp[m][n]",
    },
    {
        "title": "Word Frequency", "difficulty": "Hard", "time_limit": 5, "memory_limit": 256,
        "description": "Print each unique word and its count, sorted alphabetically, as 'word count'.\n\nExample:\nInput: the cat sat on the mat the cat\nOutput:\ncat 2\nmat 1\non 1\nsat 1\nthe 3",
        "constraints": "1 <= words <= 10^4",
        "test_cases": [
            {"input": "the cat sat on the mat the cat", "output": "cat 2\nmat 1\non 1\nsat 1\nthe 3", "function_name": "solution"},
            {"input": "hello world hello",              "output": "hello 2\nworld 1",                 "function_name": "solution"},
            {"input": "a b c a b a",                   "output": "a 3\nb 2\nc 1",                    "function_name": "solution"},
            {"input": "one",                           "output": "one 1",                            "function_name": "solution"},
        ],
        "solution": "def solution(s):\n    from collections import Counter\n    c=Counter(s.split())\n    return '\\n'.join(f'{w} {n}' for w,n in sorted(c.items()))",
    },
]


def seed():
    existing = col.count_documents({})
    if existing > 0:
        print(f"Dropping {existing} existing problems and re-seeding...")
        col.delete_many({})
    result = col.insert_many(PROBLEMS)
    print(f"\n✅ Seeded {len(result.inserted_ids)} problems:\n")
    for p in PROBLEMS:
        print(f"  [{p['difficulty']:6}]  {p['title']}")


if __name__ == "__main__":
    seed()
