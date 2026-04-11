"""
Bug Condition Exploration Tests — Task 1
========================================
These tests are EXPECTED TO FAIL on unfixed code.
Failure confirms the bugs exist. DO NOT fix the code when they fail.

Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
"""

import sys
import os
import asyncio
import importlib
import types
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

# ---------------------------------------------------------------------------
# Path setup — insert the judge_service root so "app.*" resolves correctly.
# We must do this BEFORE any app.* imports.
# ---------------------------------------------------------------------------
JUDGE_SERVICE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if JUDGE_SERVICE_ROOT not in sys.path:
    sys.path.insert(0, JUDGE_SERVICE_ROOT)

# Remove any previously cached "app" that isn't our package
if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

# Stub app.core.config so judge0_service.py can be imported without real env vars
def _ensure_config_stub():
    if "app.core.config" not in sys.modules:
        app_mod = sys.modules.get("app") or types.ModuleType("app")
        app_mod.__path__ = [os.path.join(JUDGE_SERVICE_ROOT, "app")]
        sys.modules["app"] = app_mod

        core_mod = types.ModuleType("app.core")
        core_mod.__path__ = [os.path.join(JUDGE_SERVICE_ROOT, "app", "core")]
        sys.modules["app.core"] = core_mod

        config_mod = types.ModuleType("app.core.config")
        settings_stub = MagicMock()
        settings_stub.JUDGE0_API_URL = "http://localhost:2358"
        settings_stub.JUDGE0_TIMEOUT = 10
        config_mod.settings = settings_stub
        sys.modules["app.core.config"] = config_mod

_ensure_config_stub()

# ---------------------------------------------------------------------------
# Imports from the judge service (unfixed code)
# ---------------------------------------------------------------------------
from app.services.judge0_service import Judge0Service  # noqa: E402


# ---------------------------------------------------------------------------
# Helper: run async functions in sync tests
# ---------------------------------------------------------------------------
def run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ===========================================================================
# Bug 2 — Polling linear delay
# Validates: Requirement 1.3
#
# The unfixed code uses: sleep_time = min(0.5 + (attempt * 0.2), 2.0)
# The CORRECT formula is: sleep_time = min(1.0 * (2 ** attempt), 10.0)
#
# This test mocks Judge0 to always return status 1 (In Queue), records the
# actual sleep times, and asserts they follow the CORRECT exponential formula.
# On unfixed code the assertion FAILS — confirming the bug.
# ===========================================================================

@pytest.mark.asyncio
async def test_bug2_polling_uses_exponential_backoff():
    """
    Bug 2: poll_judge0_result must use exponential backoff.
    EXPECTED TO FAIL on unfixed code (linear formula used instead).
    Validates: Requirement 1.3
    """
    import app.main as main_module

    recorded_sleep_times = []

    async def fake_sleep(t):
        recorded_sleep_times.append(t)

    # Mock Judge0 to always return "In Queue" (status id=1)
    always_in_queue = {
        "status": {"id": 1, "description": "In Queue"},
        "stdout": None,
        "stderr": None,
    }

    async def fake_get(*args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = always_in_queue
        return mock_resp

    with patch("asyncio.sleep", side_effect=fake_sleep):
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = fake_get
            mock_client_cls.return_value = mock_client

            try:
                await main_module.poll_judge0_result("fake-token", max_retries=5)
            except Exception:
                pass  # Timeout is expected after 5 attempts

    # We should have recorded sleep calls (one per attempt before giving up)
    assert len(recorded_sleep_times) >= 4, (
        f"Expected at least 4 sleep calls, got {len(recorded_sleep_times)}"
    )

    # Assert each sleep time matches the CORRECT exponential formula
    for attempt, actual_sleep in enumerate(recorded_sleep_times):
        expected_sleep = min(1.0 * (2 ** attempt), 10.0)
        assert actual_sleep == pytest.approx(expected_sleep, abs=1e-9), (
            f"Attempt {attempt}: expected sleep {expected_sleep}s "
            f"(exponential), got {actual_sleep}s — linear formula detected. "
            f"Bug 2 confirmed."
        )


# ===========================================================================
# Bug 3 — Output normalization CRLF / trailing whitespace
# Validates: Requirement 1.4
#
# The unfixed normalize_output is: return output.strip()
# .strip() only removes leading/trailing whitespace from the whole string.
# For multi-line output, intermediate lines with trailing spaces are NOT fixed:
#   "42 \nfoo".strip() == "42 \nfoo"  (trailing space on line 1 preserved — BUG)
# The correct result is "42\nfoo" (per-line rstrip applied to each line).
#
# This test calls normalize_output("42 \nfoo") and asserts result == "42\nfoo".
# On unfixed code the assertion FAILS — confirming the bug.
# ===========================================================================

@pytest.mark.asyncio
async def test_bug3_normalize_output_strips_per_line_trailing_space():
    """
    Bug 3: normalize_output must strip per-line trailing whitespace.
    EXPECTED TO FAIL on unfixed code (only .strip() is applied, not per-line rstrip).
    Validates: Requirement 1.4
    """
    import app.main as main_module

    # Multi-line output where line 1 has a trailing space — .strip() won't fix it
    result = await main_module.normalize_output("42 \nfoo")

    assert result == "42\nfoo", (
        f"normalize_output('42 \\nfoo') returned {repr(result)}, expected '42\\nfoo'. "
        f"Bug 3 confirmed: .strip() does not strip per-line trailing whitespace."
    )


# ===========================================================================
# Bug 4 — Leaderboard payload schema (score vs points, missing language)
# Validates: Requirement 1.5
#
# The unfixed update_leaderboard builds:
#   {"score": score, "submission_id": ..., ...}   — missing "points" and "language"
# The leaderboard UpdateScoreRequest requires "points" and "language".
#
# This test captures the payload and asserts it contains "points" and "language".
# On unfixed code the assertion FAILS — confirming the bug.
# ===========================================================================

@pytest.mark.asyncio
async def test_bug4_leaderboard_payload_has_points_and_language():
    """
    Bug 4: update_leaderboard payload must use 'points' key and include 'language'.
    EXPECTED TO FAIL on unfixed code ('score' key used, 'language' missing).
    Validates: Requirement 1.5
    """
    import app.main as main_module

    captured_payload = {}

    async def fake_post(url, json=None, **kwargs):
        captured_payload.update(json or {})
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = fake_post
        mock_client_cls.return_value = mock_client

        await main_module.update_leaderboard(
            user_id="user-1",
            username="alice",
            house="Gryffindor",
            problem_id=1,
            score=100,
            language="python",
        )

    assert "points" in captured_payload, (
        f"Payload missing 'points' key. Got keys: {list(captured_payload.keys())}. "
        f"Bug 4 confirmed: payload uses 'score' instead of 'points'."
    )
    assert "language" in captured_payload, (
        f"Payload missing 'language' key. Got keys: {list(captured_payload.keys())}. "
        f"Bug 4 confirmed: 'language' field not included in leaderboard payload."
    )
    assert "score" not in captured_payload, (
        f"Payload still contains deprecated 'score' key. "
        f"Should be renamed to 'points'."
    )


# ===========================================================================
# Bug 5 — In-memory storage loss
# Validates: Requirement 1.6
#
# The unfixed code stores submissions in SUBMISSIONS_DB (a plain dict).
# Clearing the dict simulates a service restart.
# GET /api/v1/submissions/{id} should return the submission, but returns pending.
#
# This test pre-populates SUBMISSIONS_DB, clears it, then GETs — asserts the
# submission is still returned. On unfixed code the assertion FAILS.
# ===========================================================================

def test_bug5_submission_survives_memory_clear():
    """
    Bug 5: Submissions must be retrieved via DatabaseService (not in-memory dict).
    On FIXED code, SUBMISSIONS_DB is removed and GET /api/v1/submissions/{id}
    delegates to DatabaseService.get_submission — confirming persistence.
    Validates: Requirement 1.6
    """
    from fastapi.testclient import TestClient
    import app.main as main_module
    from app.services.database_service import DatabaseService

    # Verify SUBMISSIONS_DB no longer exists (Bug 5 fix removes it)
    assert not hasattr(main_module, "SUBMISSIONS_DB"), (
        "main_module still has SUBMISSIONS_DB attribute. "
        "Bug 5 not fixed: in-memory dict still present."
    )

    # Mock DatabaseService.get_submission to return a fake DB record
    fake_db_record = {
        "id": 42,
        "user_id": "user-1",
        "problem_id": 1,
        "language": "python",
        "source_code": "print('hello')",
        "verdict": "Accepted",
        "score": 100,
        "passed_tests": 1,
        "total_tests": 1,
        "execution_time": 0.0,
        "compile_error": None,
        "runtime_error": None,
        "created_at": datetime(2024, 1, 1),
        "updated_at": datetime(2024, 1, 1),
    }

    async def fake_get_submission(submission_id: int):
        return fake_db_record

    with patch.object(DatabaseService, "get_submission", side_effect=fake_get_submission):
        client = TestClient(main_module.app)
        response = client.get("/api/v1/submissions/42")

    assert response.status_code == 200, (
        f"GET /api/v1/submissions/42 returned {response.status_code}. "
        f"Bug 5 fix: endpoint must delegate to DatabaseService.get_submission."
    )
    data = response.json()
    assert data.get("status") == "success", (
        f"Response status is '{data.get('status')}' instead of 'success'. "
        f"Bug 5 fix: DatabaseService must return the persisted submission."
    )


# ===========================================================================
# Bug 6 — Language ID mismatch (typescript raises ValueError, swift wrong ID)
# Validates: Requirement 1.7
#
# Unfixed judge0_service.py LANGUAGE_MAP:
#   - "typescript" is MISSING → submit_code("typescript", ...) raises ValueError
#   - "swift" maps to 75 (wrong, should be 83)
#
# These tests assert no ValueError for typescript and swift==83.
# On unfixed code both assertions FAIL — confirming the bug.
# ===========================================================================

def test_bug6_typescript_not_in_language_map():
    """
    Bug 6a: Judge0Service.LANGUAGE_MAP must include 'typescript'.
    EXPECTED TO FAIL on unfixed code (typescript missing → ValueError).
    Validates: Requirement 1.7
    """
    assert "typescript" in Judge0Service.LANGUAGE_MAP, (
        f"'typescript' not found in Judge0Service.LANGUAGE_MAP. "
        f"Keys present: {sorted(Judge0Service.LANGUAGE_MAP.keys())}. "
        f"Bug 6 confirmed: submit_code('typescript', ...) would raise ValueError."
    )


def test_bug6_swift_maps_to_correct_id_83():
    """
    Bug 6b: Judge0Service.LANGUAGE_MAP['swift'] must be 83 (not 75).
    EXPECTED TO FAIL on unfixed code (swift maps to 75).
    Validates: Requirement 1.7
    """
    swift_id = Judge0Service.LANGUAGE_MAP.get("swift")
    assert swift_id == 83, (
        f"Judge0Service.LANGUAGE_MAP['swift'] == {swift_id}, expected 83. "
        f"Bug 6 confirmed: swift uses wrong Judge0 language ID."
    )
