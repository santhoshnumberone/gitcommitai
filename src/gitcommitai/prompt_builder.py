from pathlib import Path

def fill_prompt(template_path: Path, diff_path: Path, output_path: Path) -> None:
    """
    Reads a template and diff file, substitutes {{DIFF_SUMMARY}} in template with diff content,
    and writes the final prompt to output_path.
    """
    if not template_path.exists():
        raise FileNotFoundError(f"❌ Missing template: {template_path}")
    if not diff_path.exists():
        raise FileNotFoundError(f"❌ Missing diff: {diff_path}")

    template = template_path.read_text().strip()
    diff = diff_path.read_text().strip()

    filled_prompt = template.replace("{{DIFF_SUMMARY}}", diff)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(filled_prompt)
    print(f"✅ Prompt saved to {output_path}")

if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[1]
    fill_prompt(
        template_path=ROOT / "templates" / "prompt_template.txt",
        diff_path=ROOT / "outputs" / "parsed_diff.txt",
        output_path=ROOT / "outputs" / "filled_prompt.txt"
    )
