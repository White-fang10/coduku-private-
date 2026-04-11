-- CODUKU Database Initialization
-- Creates all tables and inserts sample data

-- Create problems table
CREATE TABLE IF NOT EXISTS problems (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(50),
    score INTEGER DEFAULT 100,
    time_limit FLOAT DEFAULT 5.0,
    memory_limit INTEGER DEFAULT 256,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create test_cases table
CREATE TABLE IF NOT EXISTS test_cases (
    id SERIAL PRIMARY KEY,
    problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),
    house VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    problem_id INTEGER NOT NULL,
    language VARCHAR(50) NOT NULL,
    source_code TEXT NOT NULL,
    verdict VARCHAR(50) DEFAULT 'Pending',
    score INTEGER DEFAULT 0,
    passed_tests INTEGER DEFAULT 0,
    total_tests INTEGER DEFAULT 0,
    execution_time FLOAT DEFAULT 0.0,
    compile_error TEXT,
    runtime_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create leaderboard table
CREATE TABLE IF NOT EXISTS leaderboard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_score INTEGER DEFAULT 0,
    problems_solved INTEGER DEFAULT 0,
    ranking INTEGER,
    last_submission TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample problems (only if table is empty)
INSERT INTO problems (title, description, difficulty, score, time_limit, memory_limit)
SELECT * FROM (VALUES
    ('Two Sum', 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.', 'Easy', 10, 5.0, 256),
    ('Reverse String', 'Write a function that reverses a string. The input string is given as a sequence of characters.', 'Easy', 8, 5.0, 256),
    ('Palindrome Number', 'Given an integer x, return True if x is a palindrome integer. An integer is a palindrome when it reads the same forwards and backwards.', 'Easy', 10, 5.0, 256),
    ('Valid Parentheses', 'Given a string s containing just the characters (, ), {, }, [ and ], determine if the input string is valid.', 'Medium', 15, 5.0, 256),
    ('Fibonacci Number', 'The Fibonacci numbers form a sequence where each number is the sum of the two preceding ones. Given n, return F(n).', 'Easy', 12, 5.0, 256),
    ('FizzBuzz', 'Given an integer n, for each from 1 to n: print Fizz if divisible by 3, Buzz if divisible by 5, FizzBuzz if both, otherwise the number.', 'Easy', 8, 5.0, 256),
    ('Sum of Digits', 'Given a non-negative integer n, find the sum of its digits.', 'Easy', 6, 5.0, 256),
    ('Maximum of Array', 'Given an array of integers, find and print the maximum element.', 'Easy', 6, 5.0, 256)
) AS v(title, description, difficulty, score, time_limit, memory_limit)
WHERE NOT EXISTS (SELECT 1 FROM problems LIMIT 1);

-- Insert test cases for problems (only if test_cases is empty)
INSERT INTO test_cases (problem_id, input, output, visible)
SELECT * FROM (VALUES
    -- Two Sum
    (1, E'2 7 11 15\n9', '0 1', true),
    (1, E'3 2 4\n6', '1 2', true),
    (1, E'3 3\n6', '0 1', false),
    -- Reverse String
    (2, 'hello', 'olleh', true),
    (2, 'Hannah', 'hannaH', true),
    (2, 'world', 'dlrow', false),
    -- Palindrome Number
    (3, '121', 'True', true),
    (3, '-121', 'False', true),
    (3, '10', 'False', false),
    -- Valid Parentheses
    (4, '()[]{}', 'True', true),
    (4, '(]', 'False', true),
    (4, '([)]', 'False', false),
    -- Fibonacci
    (5, '2', '1', true),
    (5, '3', '2', true),
    (5, '4', '3', false),
    -- FizzBuzz
    (6, '5', E'1\n2\nFizz\n4\nBuzz', true),
    (6, '3', E'1\n2\nFizz', true),
    (6, '1', '1', false),
    -- Sum of Digits
    (7, '123', '6', true),
    (7, '9999', '36', true),
    (7, '0', '0', false),
    -- Maximum of Array
    (8, '3 1 4 1 5 9 2 6', '9', true),
    (8, '10 20 30', '30', true),
    (8, '-1 -5 -3', '-1', false)
) AS v(problem_id, input, output, visible)
WHERE NOT EXISTS (SELECT 1 FROM test_cases LIMIT 1);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_problem_id ON submissions(problem_id);
CREATE INDEX IF NOT EXISTS idx_submissions_verdict ON submissions(verdict);
CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at);
CREATE INDEX IF NOT EXISTS idx_leaderboard_score ON leaderboard(total_score DESC);
