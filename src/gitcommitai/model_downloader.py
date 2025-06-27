import sys
import urllib.request
from pathlib import Path

# Dict of Phi-3 quantization formats and download URLs
PHI3_MODELS = {
    "IQ3_S (Low RAM, ~1.68GB, good quality)": "https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-IQ3_S.gguf?download=true",
    "Q4_K_M (Medium RAM, ~2.39GB, very good quality)": "https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-Q4_K_M.gguf?download=true",
    "Q6_K (Higher RAM, ~3.13GB, best quality)": "https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct-Q6_K.gguf?download=true"
}


def interactive_model_selector(models_dict: dict, default_selection=("IQ3_S", "Q4_K_M")) -> str:
    print("\n📦 GitCommitAI Model Setup")
    print("Choose one or more Phi-3 quant formats to download:")

    keys = list(models_dict.keys())
    for i, key in enumerate(keys, start=1):
        quant = key.split()[0]
        is_default = any(quant == d for d in default_selection)
        print(f"{i}. {key} {'(✓)' if is_default else ''}")

    print("\nPress Enter to download the recommended defaults.")
    print("Or enter comma-separated numbers to choose manually (e.g., 1,3):")

    user_input = input("Your choice: ").strip()

    if not user_input:
        selected_indices = [i for i, k in enumerate(keys) if any(d in k for d in default_selection)]
    else:
        try:
            selected_indices = [int(i.strip()) - 1 for i in user_input.split(",")]
            assert all(0 <= i < len(keys) for i in selected_indices)
        except Exception:
            print("❌ Invalid input. Exiting.")
            sys.exit(1)

    if not selected_indices:
        print("❌ At least one model must be selected.")
        sys.exit(1)

    selected = [keys[i] for i in selected_indices]
    print("\n📥 Downloading selected model(s):")
    model_dir = Path(__file__).resolve().parents[1] / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    for s in selected:
        url = models_dict[s]
        filename = url.split("/")[-1].split("?")[0]
        save_path = model_dir / filename

        if save_path.exists():
            print(f"✅ {filename} already exists. Skipping.")
            continue

        print(f"⬇️ Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, save_path)
            print(f"✅ Saved to {save_path}")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")

    # Return quant name like "Q4_K_M"
    selected_quant = selected[0].split()[0]
    return selected_quant


def main():
    # Simple test hook
    selected_quant = interactive_model_selector(PHI3_MODELS)
    print(f"\nSelected quantization format: {selected_quant}")


if __name__ == "__main__":
    main()
