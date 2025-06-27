import subprocess


def get_git_diff():
    """Returns the staged Git diff."""
    try:
        diff = subprocess.check_output(["git", "diff", "--cached"], text=True)
        return diff.strip()
    except subprocess.CalledProcessError:
        print("❌ Failed to get staged git diff")
        return ""


def get_raw_diff():
    """Returns the full (unstaged + staged) Git diff."""
    try:
        diff = subprocess.check_output(["git", "diff"], text=True)
        return diff.strip()
    except subprocess.CalledProcessError:
        print("❌ Failed to get git diff")
        return ""
