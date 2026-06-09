from mcp_instance import mcp
from pathlib import Path
import yaml
import re
from config import VAULT_ROOT, MAX_FILE_SIZE_KB

# -- Helpers --

def safe_path(relative: str) -> Path:
    """Resolve a vault-relative path and verify it stays inside VAULT_ROOT."""
    resolved = (VAULT_ROOT / relative).resolve()
    vault_resolved = VAULT_ROOT.resolve()
    if not str(resolved).startswith(str(vault_resolved)):
        raise ValueError(f"Path '{relative}' escapes vault root")
    if not resolved.exists():
        raise FileNotFoundError(f"'{relative}' not found in vault")
    return resolved

def parse_file(path: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, markdown_body)."""
    text = path.read_text(encoding="utf-8-sig")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            _, fm_raw, body = parts
            frontmatter = yaml.safe_load(fm_raw) or {}
            return frontmatter, body.strip()
    return {}, text.strip()

def extract_sections(body: str, sections: list[str]) -> str:
    """Return only the specified ## sections from a Markdown body."""
    pattern = re.compile(r"^(#{1,3} .+)$", re.MULTILINE)
    headers = [(m.start(), m.group()) for m in pattern.finditer(body)]
    result = []
    for i, (start, header) in enumerate(headers):
        heading_text = re.sub(r"^#+\s+", "", header)
        if heading_text in sections:
            end = headers[i + 1][0] if i + 1 < len(headers) else len(body)
            result.append(body[start:end].strip())
    return "\n\n".join(result)

# -- Tools --

@mcp.tool()
def list_context_files(
    folder: str | None = None,
    status: str | None = None,
    tags: list[str] | None = None,
    include_summary: bool = True
) -> list[dict]:
    """List files in the vault, optionally filtered by folder, status, or tags."""
    root = (VAULT_ROOT / folder).resolve() if folder else VAULT_ROOT.resolve()
    results = []
    for md_file in root.rglob("*.md"):
        try:
            fm, body = parse_file(md_file)
        except Exception:
            continue
        if status and fm.get("status") != status:
            continue
        if tags and not all(t in fm.get("tags", []) for t in tags):
            continue
        entry = {
            "path": md_file.relative_to(VAULT_ROOT).as_posix(),
            "title": fm.get("title", md_file.stem),
            "status": fm.get("status"),
            "tags": fm.get("tags", []),
            "updated": str(fm.get("updated", "")),
        }
        if include_summary:
            entry["summary"] = extract_sections(body, ["Summary"]) or None
        results.append(entry)
    return results

@mcp.tool()
def read_context_file(
    path: str,
    sections: list[str] | None = None,
) -> dict:
    """Read a single context file by vault-relative path."""
    try:
        p = safe_path(path)
        size_kb = p.stat().st_size / 1024
        fm, body = parse_file(p)

        if size_kb > MAX_FILE_SIZE_KB:
            summary = extract_sections(body, ["Summary"]) or None
            return {
                "warning": f"File is {size_kb:.0f} KB (limit {MAX_FILE_SIZE_KB} KB). Returning Summary only.",
                "frontmatter": fm,
                "content": summary,
            }

        if sections:
            body = extract_sections(body, sections)
        
        return {"frontmatter": fm, "content": body}
    
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error reading '{path}': {e}"}

@mcp.tool()
def read_active_context(
    max_files: int = 10,
    include_sections: list[str] | None = None,
) -> list[dict]:
    """Read all files with status: active, ordered by priority then updated."""
    from config import ACTIVE_STATUSES

    all_files = []
    for md_file in VAULT_ROOT.rglob("*.md"):
        try:
            fm, body = parse_file(md_file)
        except Exception:
            continue
        if fm.get("status") not in ACTIVE_STATUSES:
            continue
        all_files.append((md_file, fm, body))

    # Sort: priority (high->medium->low->None), then updated descending
    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_files.sort(key=lambda x: (
        priority_order.get(x[1].get("priority"), 3),
        str(x[1].get("updated", "")),
    ), reverse=False)
    
    results = []
    for md_file, fm, body in all_files[:max_files]:
        if include_sections:
            body = extract_sections(body, include_sections)
        size_kb = md_file.stat().st_size / 1024
        if size_kb > MAX_FILE_SIZE_KB:
            summary = extract_sections(body, ["Summary"]) or "(no Summary section)"
            results.append({
                "path": md_file.relative_to(VAULT_ROOT).as_posix(),
                "warning": f"File is {size_kb:.0f} KB, returning Summary only.",
                "frontmatter": fm,
                "content": summary,
            })
        else:
            results.append({
                "path": md_file.relative_to(VAULT_ROOT).as_posix(),
                "frontmatter": fm,
                "content": body,
            })
    return results

@mcp.tool()
def read_raw_file(
    path: str,
    max_kb: float | None = None,
) -> dict:
    """Read any file in the vault as raw text, without frontmatter parsing.
    Useful for .txt, .csv, and other non-markdown files. max_kb overrides
    the default MAX_FILE_SIZE_KB limit if you need to read a larger file."""
    try:
        resolved = (VAULT_ROOT / path).resolve()
        vault_resolved = VAULT_ROOT.resolve()
        if not str(resolved).startswith(str(vault_resolved)):
            return {"error": f"Path '{path}' escapes vault root"}
        if not resolved.exists():
            return {"error": f"'{path}' not found in vault"}

        size_kb = resolved.stat().st_size / 1024
        limit = max_kb if max_kb is not None else MAX_FILE_SIZE_KB

        if size_kb > limit:
            return {
                "error": f"File is {size_kb:.1f} KB, which exceeds the {limit} KB limit. Pass a larger max_kb to override."
            }

        content = resolved.read_text(encoding="utf-8-sig")
        return {
            "path": path,
            "size_kb": round(size_kb, 1),
            "content": content,
        }

    except UnicodeDecodeError:
        return {"error": f"'{path}' is not a text file or uses an unsupported encoding"}
    except Exception as e:
        return {"error": f"Unexpected error reading '{path}': {e}"}
