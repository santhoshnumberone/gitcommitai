import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from gitcommitai.diff_profiler import classify_diff_size
from gitcommitai.profile_manager import get_profile_config, PROFILE_HINTS
from gitcommitai.cache_manager import load_cache, save_cache, is_cache_valid
from gitcommitai.llm_infer import run_llm, load_prompt
from gitcommitai.model_downloader import interactive_model_selector, PHI3_MODELS
from gitcommitai.diff_extractor import get_git_diff

from gitcommitai.commit_write import handle_commit_flow

VERSION = "1.0.0"

ROOT_DIR = Path(__file__).resolve().parents[1]
PROMPT_TEMPLATE_PATH = ROOT_DIR / "templates" / "prompt_template.txt"
MODEL_DIR = ROOT_DIR / "models"
CACHE_PATH = ROOT_DIR / ".gitcommitai" / "cache.json"


def log(msg, verbose=False, quiet=False, always=False):
    if always or (not quiet and (verbose or not msg.startswith("✔"))):
        print(msg)


def cli():
    parser = argparse.ArgumentParser(description="GitCommitAI+: Local-first Git commit assistant powered by LLMs")
    parser.add_argument("--confirm", action="store_true", help="Confirm and write the commit")
    parser.add_argument("--edit", action="store_true", help="Edit the message before committing")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't write commit")
    parser.add_argument("--profile", default="auto", help="System profile to use")
    parser.add_argument("--model", help="Path to model (overrides profile)")
    parser.add_argument("--reset-model-selection", action="store_true", help="Reset model selection and choose again")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-essential output")
    parser.add_argument("--verbose", action="store_true", help="Enable extra debug info")

    args = parser.parse_args()

    if args.version:
        print(f"GitCommitAI+ version {VERSION}")
        sys.exit(0)

    # Step 1: Get Git diff
    diff = get_git_diff()
    diff_profile = classify_diff_size()
    diff_type = diff_profile.category

    # Step 2: Load or compute profile
    cache_valid = is_cache_valid(CACHE_PATH, diff_type)
    profile_config = None

    if cache_valid and not args.reset_model_selection:
        cached = load_cache(CACHE_PATH)
        profile_config = cached["profile_config"]
        log("📊 Loaded cached profile config.", verbose=args.verbose, quiet=args.quiet)
    else:
        if args.profile == "auto":
            profile_config = get_profile_config()
            log(f"⚙️  Auto-selected profile: {profile_config}", verbose=args.verbose, quiet=args.quiet)
        elif args.profile in PROFILE_HINTS:
            profile_config = PROFILE_HINTS[args.profile]
            log(f"⚙️  Using profile: {args.profile}", verbose=args.verbose, quiet=args.quiet)
        else:
            print(f"❌ Unknown profile: {args.profile}")
            sys.exit(1)

        selected_quant = interactive_model_selector(PHI3_MODELS)
        profile_config["quant"] = selected_quant

        save_cache(CACHE_PATH, {
            "profile_config": profile_config,
            "diff_type": diff_type
        })

    # Step 3: Load prompt template
    if not PROMPT_TEMPLATE_PATH.exists():
        print(f"❌ Prompt template not found: {PROMPT_TEMPLATE_PATH}")
        sys.exit(1)

    prompt_text = load_prompt(str(PROMPT_TEMPLATE_PATH)).replace("{{DIFF}}", diff)

    # Step 4: Resolve model path
    model_path = args.model
    if not model_path:
        quant = profile_config["quant"]
        model_path = MODEL_DIR / f"Phi-3-mini-4k-instruct-{quant}.gguf"

    # Step 5: Run LLM
    result = run_llm(
        model_path=str(model_path),
        prompt_text=prompt_text,
        n_ctx=profile_config["n_ctx"],
        n_threads=4,
        n_batch=profile_config["n_batch"],
        n_gpu_layers=profile_config["n_gpu_layers"]
    )

    
    handle_commit_flow(
        message=result,
        confirm=args.confirm,
        edit=args.edit,
        dry_run=args.dry_run
    )



if __name__ == "__main__":
    cli()
