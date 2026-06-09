from mcp_instance import mcp
from pathlib import Path
from datetime import date
import yaml
from config import VAULT_ROOT
from tools.read import safe_path, parse_file
from tools.helpers import write_file


# ── Tools ──────────────────────────────────────────────────────────────────

@mcp.tool()
def write_context_file(
    path: str,
    frontmatter: dict,
    content: str,
    overwrite: bool = False,
) -> dict:
    """Create or overwrite a vault file. overwrite must be True to replace an
    existing file. Sets the updated field in frontmatter to today automatically.
    After creating a new file, also update _ClaudeWorkflow/_index.md."""
    try:
        resolved = (VAULT_ROOT / path).resolve()
        vault_resolved = VAULT_ROOT.resolve()
        if not str(resolved).startswith(str(vault_resolved)):
            return {"error": f"Path '{path}' escapes vault root"}

        already_exists = resolved.exists()

        if already_exists and not overwrite:
            return {"error": f"'{path}' already exists. Pass overwrite=True to replace it."}

        frontmatter["updated"] = str(date.today())
        resolved.parent.mkdir(parents=True, exist_ok=True)
        write_file(resolved, frontmatter, content)

        return {
            "path": path,
            "created": not already_exists,
            "size_bytes": resolved.stat().st_size,
        }

    except Exception as e:
        return {"error": f"Unexpected error writing '{path}': {e}"}


@mcp.tool()
def append_to_context_file(
    path: str,
    content: str,
    section: str | None = None,
    update_timestamp: bool = True,
) -> dict:
    """Append content to an existing vault file. If section is provided, appends
    under that ## header, creating the section if it doesn't exist. If
    update_timestamp is True, updates the updated field in frontmatter to today."""
    try:
        content = content.replace("\\n", "\n").replace("\\t", "\t")
        p = safe_path(path)
        fm, body = parse_file(p)

        if section:
            header = f"## {section}"
            if header in body:
                body = body.rstrip() + f"\n\n{content}"
            else:
                body = body.rstrip() + f"\n\n{header}\n\n{content}"
        else:
            body = body.rstrip() + f"\n\n{content}"

        if update_timestamp:
            fm["updated"] = str(date.today())

        before_size = p.stat().st_size
        write_file(p, fm, body)
        after_size = p.stat().st_size

        return {
            "path": path,
            "appended_bytes": after_size - before_size,
            "new_size_bytes": after_size,
        }

    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error appending to '{path}': {e}"}
