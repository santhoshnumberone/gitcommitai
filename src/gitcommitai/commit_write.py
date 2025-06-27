# gitcommitai/commit_write.py
import subprocess
import tempfile
import os

def preview_message(message: str):
    print("\n📝 Commit message preview:")
    print(message)

def edit_message_interactively(message: str) -> str:
    """Opens a temporary editor (nano) for user to edit commit message."""
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tmp") as f:
        f.write(message)
        f.flush()
        subprocess.call(["nano", f.name])
        f.seek(0)
        edited = f.read().strip()
    os.remove(f.name)
    return edited

def run_git_commit(message: str):
    """Runs `git commit -m` with the generated (or edited) message."""
    subprocess.run(["git", "commit", "-m", message])
    print("✅ Commit completed.")

def handle_commit_flow(message: str, confirm=False, edit=False, dry_run=False):
    """
    Central function to handle:
    - preview
    - optional editing
    - optional commit
    """
    preview_message(message)

    if dry_run:
        return

    final_message = message

    if edit:
        final_message = edit_message_interactively(message)

    if confirm or edit:
        run_git_commit(final_message)

