import platform
import psutil

# Predefined profiles to override automatic detection (used via --profile flag)
PROFILE_HINTS = {
    "low": {"n_ctx": 256, "n_batch": 24, "n_gpu_layers": 0},
    "medium": {"n_ctx": 512, "n_batch": 42, "n_gpu_layers": 8},
    "high": {"n_ctx": 1024, "n_batch": 64, "n_gpu_layers": 16},
}

def get_profile_config() -> dict:
    """Returns profile configuration based on system specs (RAM, architecture)."""
    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))
    cpu_arch = platform.machine()
    is_mac = platform.system() == "Darwin"

    # Heuristics
    if ram_gb <= 8:
        profile = PROFILE_HINTS["low"]
    elif ram_gb <= 16:
        profile = PROFILE_HINTS["medium"]
    else:
        profile = PROFILE_HINTS["high"]

    # Mac with Metal tuning (e.g., for Apple Silicon)
    if is_mac and "arm" in cpu_arch.lower():
        profile["n_gpu_layers"] = 1

    return profile
