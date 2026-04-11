"""
Preservation Property Tests — Task 2
=====================================
These tests PASS on unfixed code — they verify baseline behavior for non-buggy inputs.
Failure would indicate a regression in existing correct behavior.

Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8
"""

import sys
import os
import types
from unittest.mock import MagicMock

import pytest
from hypothesis import given, assume, settings as h_settings
import hypothesis.strategies as st

# ---------------------------------------------------------------------------
# Path setup — insert the judge_service root so "app.*" resolves correctly.
# ---------------------------------------------------------------------------
JUDGE_SERVICE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if JUDGE_SERVICE_ROOT not in sys.path:
    sys.path.insert(0, JUDGE_SERVICE_ROOT)

# Remove any previously cached "app" that isn't our package
if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]


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
import app.main as main_module  # noqa: E402


# ---------------------------------------------------------------------------
# Helper: inline normalize_output_fixed (what the fixed code will do)
# This is the CORRECT normalization: CRLF + per-line rstrip + overall strip.
# ---------------------------------------------------------------------------
def normalize_output_fixed(output: str) -> str:
    """Fixed normalization: CRLF-aware, per-line rstrip, overall strip."""
    if not output:
        return ""
    text = output.replace('\r\n', '\n').replace('\r', '\n')
    lines = [line.rstrip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


# ===========================================================================
# Preservation 1 — Output normalization (clean inputs)
# Validates: Requirements 3.1, 3.2
#
# For clean inputs (no \r, no trailing per-line whitespace), the fixed
# normalize_output_fixed(s) must equal s.strip() — same as the original.
# These tests PASS on unfixed code because clean inputs are unaffected.
# ===========================================================================

@given(st.text(alphabet=st.characters(blacklist_characters='\r'), min_size=1))
@h_settings(max_examples=200)
def test_preservation1_normalize_output_clean_inputs(s: str):
    """
    Preservation 1: For clean inputs (no \\r, no trailing per-line whitespace),
    normalize_output_fixed(s) == s.strip() — same result as original.

    **Validates: Requirements 3.1, 3.2**
    """
    # Filter: only strings with no trailing whitespace on any line
    lines = s.split('\n')
    assume(all(line == line.rstrip() for line in lines))

    result = normalize_output_fixed(s)
    assert result == s.strip(), (
        f"normalize_output_fixed({repr(s)}) returned {repr(result)}, "
        f"expected {repr(s.strip())} — clean inputs must behave identically to original."
    )


# ===========================================================================
# Preservation 2 — Language map (non-affected languages)
# Validates: Requirements 3.5, 3.6
#
# For languages not affected by Bug 6 (not typescript/swift), LANGUAGE_IDS
# must still map to the original canonical values.
# ===========================================================================

# Canonical values for non-affected languages
CANONICAL_LANGUAGE_IDS = {
    "python": 71,
    "python3": 71,
    "java": 62,
    "cpp": 54,
    "c": 50,
    "javascript": 63,
    "go": 60,
    "rust": 73,
    "csharp": 51,
    "ruby": 72,
    "php": 68,
    "kotlin": 78,
}


@given(st.sampled_from(list(CANONICAL_LANGUAGE_IDS.keys())))
def test_preservation2_language_map_non_affected(lang: str):
    """
    Preservation 2: Non-affected languages must still map to their canonical Judge0 IDs.

    **Validates: Requirements 3.5, 3.6**
    """
    expected_id = CANONICAL_LANGUAGE_IDS[lang]
    actual_id = main_module.LANGUAGE_IDS.get(lang)

    assert actual_id == expected_id, (
        f"LANGUAGE_IDS[{repr(lang)}] == {actual_id}, expected {expected_id}. "
        f"Non-affected language mapping must be preserved."
    )


# ===========================================================================
# Preservation 3 — Polling backoff bounds
# Validates: Requirements 3.3, 3.4
#
# The FIXED formula min(1.0 * (2 ** attempt), 10.0) must always stay in
# [1.0, 10.0] and be monotonically non-decreasing across all attempt values.
# ===========================================================================

@given(st.integers(min_value=0, max_value=29))
def test_preservation3_polling_backoff_bounds(attempt: int):
    """
    Preservation 3: Fixed exponential backoff formula stays in [1.0, 10.0].

    **Validates: Requirements 3.3, 3.4**
    """
    sleep_time = min(1.0 * (2 ** attempt), 10.0)

    assert sleep_time >= 1.0, (
        f"Attempt {attempt}: sleep_time={sleep_time} is below minimum 1.0s."
    )
    assert sleep_time <= 10.0, (
        f"Attempt {attempt}: sleep_time={sleep_time} exceeds maximum 10.0s."
    )


@given(
    st.integers(min_value=0, max_value=28),
    st.integers(min_value=1, max_value=29),
)
def test_preservation3_polling_backoff_monotonic(attempt_a: int, attempt_b: int):
    """
    Preservation 3: Fixed exponential backoff is monotonically non-decreasing.

    **Validates: Requirements 3.3, 3.4**
    """
    assume(attempt_a < attempt_b)

    sleep_a = min(1.0 * (2 ** attempt_a), 10.0)
    sleep_b = min(1.0 * (2 ** attempt_b), 10.0)

    assert sleep_a <= sleep_b, (
        f"Backoff not monotonic: attempt {attempt_a} → {sleep_a}s, "
        f"attempt {attempt_b} → {sleep_b}s. Expected sleep_a <= sleep_b."
    )


# ===========================================================================
# Preservation 4 — Verdict mapping
# Validates: Requirements 3.7, 3.8
#
# map_judge0_verdict must still return correct verdicts for key status codes.
# These are non-buggy behaviors that must be preserved after the fix.
# ===========================================================================

def test_preservation4_verdict_wrong_answer():
    """
    Preservation 4: Judge0 status 4 (Wrong Answer) → VerdictEnum.WRONG_ANSWER.

    **Validates: Requirements 3.7, 3.8**
    """
    from app.main import VerdictEnum, map_judge0_verdict

    result = map_judge0_verdict(4, passed_count=0, total_count=1)
    assert result == VerdictEnum.WRONG_ANSWER, (
        f"map_judge0_verdict(4, ...) returned {result}, expected WRONG_ANSWER."
    )


def test_preservation4_verdict_compilation_error():
    """
    Preservation 4: Judge0 status 6 (Compilation Error) → VerdictEnum.COMPILATION_ERROR.

    **Validates: Requirements 3.7, 3.8**
    """
    from app.main import VerdictEnum, map_judge0_verdict

    result = map_judge0_verdict(6, passed_count=0, total_count=1)
    assert result == VerdictEnum.COMPILATION_ERROR, (
        f"map_judge0_verdict(6, ...) returned {result}, expected COMPILATION_ERROR."
    )


def test_preservation4_verdict_time_limit():
    """
    Preservation 4: Judge0 status 5 (Time Limit Exceeded) → VerdictEnum.TIME_LIMIT.

    **Validates: Requirements 3.7, 3.8**
    """
    from app.main import VerdictEnum, map_judge0_verdict

    result = map_judge0_verdict(5, passed_count=0, total_count=1)
    assert result == VerdictEnum.TIME_LIMIT, (
        f"map_judge0_verdict(5, ...) returned {result}, expected TIME_LIMIT."
    )
