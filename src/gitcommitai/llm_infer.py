import os
import sys
import argparse
import time
import json
import psutil
import contextlib
from pathlib import Path
from llama_cpp import Llama

from gitcommitai.profile_manager import get_profile_config, PROFILE_HINTS
from gitcommitai.diff_profiler import classify_diff_size
from gitcommitai.cache_manager import load_cache, save_cache, is_cache_valid

def get_ram_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def load_prompt(prompt_path: str) -> str:
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    with open(prompt_path, "r") as f:
        prompt = f.read().rstrip()
    if not prompt.endswith("Commit message:"):
        prompt += "\nCommit message:"
    return prompt

@contextlib.contextmanager
def suppress_metal_logs():
    stderr = sys.stderr
    devnull = open(os.devnull, 'w')
    sys.stderr = devnull
    try:
        yield
    finally:
        sys.stderr = stderr
        devnull.close()

def run_llm(model_path, prompt_text, n_ctx, n_threads, n_batch, n_gpu_layers,
            max_tokens=64, temperature=0.2, stop=["\n\n", "\nCommit", "User:"], use_mlock=True):

    print("⚙️ LLM Runtime Configuration:")
    print(f"  model         : {Path(model_path).name}")
    print(f"  n_ctx         : {n_ctx}")
    print(f"  n_threads     : {n_threads}")
    print(f"  n_batch       : {n_batch}")
    print(f"  n_gpu_layers  : {n_gpu_layers}")
    print(f"  use_mlock     : {use_mlock}")
    print(f"🔁 [Before load] RAM: {get_ram_usage():.2f} MB")

    load_start = time.perf_counter()
    with suppress_metal_logs():
        llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_batch=n_batch,
            n_gpu_layers=n_gpu_layers,
            use_mlock=use_mlock,
            verbose=False
        )
    load_end = time.perf_counter()

    print(f"✅ Model loaded in {load_end - load_start:.2f} seconds")
    print(f"🧠 [After load] RAM: {get_ram_usage():.2f} MB")

    print("🚀 Generating commit message...")
    infer_start = time.perf_counter()
    output = llm(prompt=prompt_text, max_tokens=max_tokens, temperature=temperature, stop=stop)
    infer_end = time.perf_counter()
    print(f"🧠 [After inference] RAM: {get_ram_usage():.2f} MB")

    duration = infer_end - infer_start
    result = output["choices"][0]["text"].strip()

    tokens_used = output.get("usage", {}).get("completion_tokens", None)
    if tokens_used is None:
        word_count = len(result.split())
        tokens_used = int(word_count * 1.3)

    tps = tokens_used / duration if duration > 0 else 0
    print(f"✅ Inference completed in {duration:.2f} sec, estimated {tokens_used} tokens ({tps:.2f} tokens/sec)")

    return result

def main():
    parser = argparse.ArgumentParser(description="Generate commit message using local LLM")

    parser.add_argument("--prompt_path", required=True, help="Path to prompt text file")
    parser.add_argument("--model", help="Path to GGUF model file (overrides profile-based model path)")
    parser.add_argument("--profile", default="auto", help="System profile to use (default: auto)")

    # Optional overrides
    parser.add_argument("--n_ctx", type=int, help="Context window size")
    parser.add_argument("--n_threads", type=int, help="CPU threads")
    parser.add_argument("--n_batch", type=int, help="Batch size")
    parser.add_argument("--n_gpu_layers", type=int, help="GPU layers")

    args = parser.parse_args()
    prompt_text = load_prompt(args.prompt_path)

    # Use project root-relative path for cache
    root_dir = Path(__file__).resolve().parents[1]
    cache_path = root_dir / ".gitcommitai" / "cache.json"

    # Fetch diff category
    diff_profile = classify_diff_size()
    diff_type = diff_profile.category

    # Load or infer profile
    if is_cache_valid(cache_path, diff_type):
        cached = load_cache(cache_path)
        profile_config = cached["profile_config"]
        print("📊 Loaded cached profile config.")
    else:
        if args.profile == "auto":
            profile_config = get_profile_config()
        elif args.profile in PROFILE_HINTS:
            profile_config = PROFILE_HINTS[args.profile]
        else:
            print(f"❌ Unknown profile: {args.profile}")
            sys.exit(1)

        save_cache(cache_path, {
            "profile_config": profile_config,
            "diff_type": diff_type
        })

    # Apply overrides
    n_ctx = args.n_ctx or profile_config["n_ctx"]
    n_threads = args.n_threads or 4
    n_batch = args.n_batch or profile_config["n_batch"]
    n_gpu_layers = args.n_gpu_layers or profile_config["n_gpu_layers"]

    # Model path resolution
    model_path = args.model
    if not model_path:
        quant = profile_config["quant"]
        model_path = root_dir / "models" / f"Phi-3-mini-4k-instruct-{quant}.gguf"

    result = run_llm(
        model_path=str(model_path),
        prompt_text=prompt_text,
        n_ctx=n_ctx,
        n_threads=n_threads,
        n_batch=n_batch,
        n_gpu_layers=n_gpu_layers
    )

    print("\n📝 Commit message:")
    print(result)

if __name__ == "__main__":
    main()
