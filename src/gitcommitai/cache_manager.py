import json
import os
from pathlib import Path
import hashlib
import platform
import psutil
import subprocess


def get_git_root():
    """Finds the root directory of the git repo."""
    try:
        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        return Path(root)
    except Exception:
        return Path.cwd()


GIT_ROOT = get_git_root()
CACHE_PATH = GIT_ROOT / ".gitcommitai" / "cache.json"
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_cache():
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}


def save_cache(data):
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def hash_diff_text(diff_text):
    return hashlib.md5(diff_text.encode("utf-8")).hexdigest()


def get_system_signature():
    return {
        "ram_gb": round(psutil.virtual_memory().total / (1024 ** 3)),
        "cpu_arch": platform.machine(),
        "platform": platform.system(),
        "python_version": platform.python_version(),
    }


def is_profile_changed(current_diff_hash, current_system_signature):
    cache = load_cache()
    last_diff_hash = cache.get("last_diff_hash")
    last_sys_signature = cache.get("last_system_signature")

    return last_diff_hash != current_diff_hash or last_sys_signature != current_system_signature


def update_cache(diff_hash, system_signature):
    save_cache({
        "last_diff_hash": diff_hash,
        "last_system_signature": system_signature
    })
