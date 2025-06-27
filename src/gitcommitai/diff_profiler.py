"""
diff_profiler.py

Analyzes staged Git diffs and classifies them by size to optimize LLM inference
parameters like context window and batch size.
"""

import subprocess
from dataclasses import dataclass
from typing import Literal

DiffCategory = Literal[
    "very_tiny", "tiny", "very_small", "small", "medium",
    "large", "very_large", "huge", "very_huge"
]

@dataclass
class DiffProfile:
    category: DiffCategory
    lines_changed: int
    chars_changed: int
    runtime_hint: dict  # Example: {"n_ctx": 256, "n_batch": 42}


def get_git_diff_stats() -> tuple[int, int]:
    """Returns number of lines and characters changed in the staged git diff."""
    try:
        diff_output = subprocess.check_output(
            ["git", "diff", "--cached"], stderr=subprocess.DEVNULL
        ).decode("utf-8")
    except subprocess.CalledProcessError:
        return 0, 0

    lines_changed = diff_output.count("\n")
    chars_changed = len(diff_output)
    return lines_changed, chars_changed


def classify_diff(lines: int, chars: int) -> DiffCategory:
    if lines < 5 and chars < 200:
        return "very_tiny"
    elif lines < 10 and chars < 400:
        return "tiny"
    elif lines < 20:
        return "very_small"
    elif lines < 40:
        return "small"
    elif lines < 80:
        return "medium"
    elif lines < 160:
        return "large"
    elif lines < 300:
        return "very_large"
    elif lines < 500:
        return "huge"
    else:
        return "very_huge"


def get_runtime_hint(category: DiffCategory) -> dict:
    """Returns recommended LLM runtime parameters based on diff size category."""
    table = {
        "very_tiny": {"n_ctx": 128, "n_batch": 16},
        "tiny": {"n_ctx": 128, "n_batch": 24},
        "very_small": {"n_ctx": 192, "n_batch": 32},
        "small": {"n_ctx": 256, "n_batch": 42},
        "medium": {"n_ctx": 384, "n_batch": 50},
        "large": {"n_ctx": 512, "n_batch": 64},
        "very_large": {"n_ctx": 768, "n_batch": 80},
        "huge": {"n_ctx": 1024, "n_batch": 90},
        "very_huge": {"n_ctx": 2048, "n_batch": 100},
    }
    return table.get(category, {"n_ctx": 256, "n_batch": 42})


def classify_diff_size() -> DiffProfile:
    """Analyzes staged diff and returns profile containing size and runtime hints."""
    lines, chars = get_git_diff_stats()
    category = classify_diff(lines, chars)
    runtime_hint = get_runtime_hint(category)
    return DiffProfile(category, lines, chars, runtime_hint)


__all__ = [
    "DiffProfile",
    "DiffCategory",
    "classify_diff_size",
    "get_git_diff_stats"
]
