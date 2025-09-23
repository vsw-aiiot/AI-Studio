import markdown
from pathlib import Path

def convert_to_markdown(content: str, file_name: str = "output.md") -> str:
    """
    Converts plain text (or Markdown-compatible text) to HTML and saves .md file.
    Returns file path.
    """
    # Save raw markdown content
    output_path = Path("generated") / file_name
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(output_path)

# Optional usage
if __name__ == "__main__":
    test_text = "# Sample Output\n\nThis is a demo of **Markdown** file generation."
    path = convert_to_markdown(test_text)
    print(f"Markdown saved to: {path}")
