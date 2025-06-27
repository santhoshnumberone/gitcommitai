import pytest
from gitcommitai.diff_profiler import (
    classify_diff,
    get_runtime_hint,
    classify_diff_size,
    DiffProfile,
)

@pytest.mark.parametrize(
    "lines, chars, expected_category",
    [
        (2, 100, "very_tiny"),
        (8, 300, "tiny"),
        (15, 500, "very_small"),
        (30, 1000, "small"),
        (60, 2000, "medium"),
        (140, 3000, "large"),
        (250, 6000, "very_large"),
        (450, 9000, "huge"),
        (600, 12000, "very_huge"),
    ]
)
def test_classify_diff(lines, chars, expected_category):
    assert classify_diff(lines, chars) == expected_category

def test_get_runtime_hint_returns_valid_config():
    categories = [
        "very_tiny", "tiny", "very_small", "small", "medium",
        "large", "very_large", "huge", "very_huge"
    ]
    for cat in categories:
        hint = get_runtime_hint(cat)
        assert "n_ctx" in hint and isinstance(hint["n_ctx"], int)
        assert "n_batch" in hint and isinstance(hint["n_batch"], int)

def test_classify_diff_size_structure():
    profile = classify_diff_size()
    assert isinstance(profile, DiffProfile)
    assert profile.category in {
        "very_tiny", "tiny", "very_small", "small", "medium",
        "large", "very_large", "huge", "very_huge"
    }
    assert isinstance(profile.lines_changed, int)
    assert isinstance(profile.chars_changed, int)
    assert isinstance(profile.runtime_hint, dict)

