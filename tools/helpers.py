from pathlib import Path
import yaml

def write_file(path: Path, frontmatter: dict, body: str) -> None:
    """Write frontmatter + body with LF line endings (Obsidian preference)."""
    body = body.replace("\\n", "\n").replace("\\t", "\t")
    fm_yaml = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    content = f"---\n{fm_yaml}---\n\n{body}\n"
    path.write_bytes(content.encode("utf-8"))
