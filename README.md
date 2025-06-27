# GitCommitAI+ 💬⚡ 


---

## ✨ Features

- 🧠 **AI-powered messages**: Uses models like M Phi-3 to generate natural, readable Git commit messages.
- 🔒 **Local-first, no cloud**: Runs completely offline with GGUF models via `llama-cpp-python`.

---

## 🛠️ Installation

Requires Python ≥ 3.9.
```bash
git clone https://github.com/yourname/gitcommitai-plus.git
cd gitcommitai-plus
make install
```
This will:
- Set up a virtual environment
- Install dependencies from requirements.txt
- Optionally download a default model (Phi-3 or Mistral GGUF)
---
## 🛠️ Usage
```bash
# Stage your files
git add .

# Generate a commit message
gitcommitai

# Preview only
gitcommitai --preview

# Edit before final commit
gitcommitai --edit

# Test mode, no commit
gitcommitai --dry-run
```

## 💡 Example
```bash
# You stage some changes
git add src/utils.py

# Run GitCommitAI+
gitcommitai --preview

# Output
# [feat] Add file type detection in utility functions
# - Added `detect_file_type()` to utils.py
# - Supports .csv, .json, .txt
```
---
## 🧩 CLI Options
| Flag |	Description |
| - | - |
| --preview |	Show generated message before committing |
| --edit |	Open message in editor for manual tweak |
| --dry-run |	Display message but skip actual commit |
| --no-context |	Skip repo metadata (branch, README, logs) context injection (Phase 2) |
| --strict |	Enforce semantic type prefixes (feat:, fix:) |
| --audit |	Scan Git log for non-semantic commits and report violations (WIP) |
---
## ✨ Example Flow
```bash
$ gitcommitai --preview
✔ Parsed staged diff
✔ Retrieved repo context
✔ Prompted LLM (Mistral)
---
Generated commit:
feat(auth): enforce token expiration logic
adds auto-expiry for JWT tokens in the login flow.
✅ Commit ready. Use --edit or press Enter to continue.
```
---
## 🧪 Development Setup
```bash
# Install virtualenv and requirements
make install

# Run CLI
make run

# Run tests
make test

# Format with black
black .
```
To use a custom model:
- Place your .gguf file in /models
- Update the config.json to point to it

---
## 🤝 Contributing
We welcome PRs, bug reports, ideas, and suggestions!
See CONTRIBUTING.md for contribution guidelines.

## 📄 License
Licensed under the Apache License 2.0.
See LICENSE for full terms.
© 2025 Santhosh Dhaipule Chandrakanth.

## ⭐️ Star the Project
If GitCommitAI+ saves you time or headaches, give it a ⭐ on GitHub to support the project!
