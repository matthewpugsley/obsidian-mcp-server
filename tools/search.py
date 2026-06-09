from mcp_instance import mcp
from config import VAULT_ROOT, MAX_FILE_SIZE_KB
from tools.read import parse_file

# ── Helpers ────────────────────────────────────────────────────────────────

def extract_snippet(content: str, query: str, context_chars: int = 120) -> str:
    """Return a short snippet of text around the first match of query."""
    lower_content = content.lower()
    lower_query = query.lower()
    idx = lower_content.find(lower_query)
    if idx == -1:
        return ""
    start = max(0, idx - context_chars // 2)
    end = min(len(content), idx + len(query) + context_chars // 2)
    snippet = content[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    return snippet


def count_matches(content: str, query: str) -> int:
    """Count case-insensitive occurrences of query in content."""
    return content.lower().count(query.lower())


# ── Tools ──────────────────────────────────────────────────────────────────

@mcp.tool()
def search_context(
    query: str,
    folder: str | None = None,
    status: str | None = None,
    max_results: int = 10,
) -> list[dict]:
    """Full-text search across the vault. Returns files containing the query
    string, ordered by number of matches descending."""
    root = (VAULT_ROOT / folder).resolve() if folder else VAULT_ROOT.resolve()
    results = []

    for md_file in root.rglob("*.md"):
        try:
            fm, body = parse_file(md_file)
        except Exception:
            continue

        if status and fm.get("status") != status:
            continue

        # Search both frontmatter values and body
        searchable = body + " " + " ".join(str(v) for v in fm.values())
        match_count = count_matches(searchable, query)

        if match_count == 0:
            continue

        results.append({
            "path": md_file.relative_to(VAULT_ROOT).as_posix(),
            "title": fm.get("title", md_file.stem),
            "status": fm.get("status"),
            "match_count": match_count,
            "snippet": extract_snippet(body, query),
        })

    results.sort(key=lambda x: x["match_count"], reverse=True)
    return results[:max_results]

@mcp.tool()
def search_raw_file(
    path: str,
    query: str,
    max_results: int = 20,
    context_lines: int = 0,
    max_kb: float | None = None,
) -> dict:
    """Search for a string within any vault file, returning matching lines with
    their line numbers. Useful for large non-markdown files like CSVs or
    tab-delimited exports where full-file reads would be too large."""
    try:
        resolved = (VAULT_ROOT / path).resolve()
        vault_resolved = VAULT_ROOT.resolve()
        if not str(resolved).startswith(str(vault_resolved)):
            return {"error": f"Path '{path}' escapes vault root"}
        if not resolved.exists():
            return {"error": f"'{path}' not found in vault"}

        size_kb = resolved.stat().st_size / 1024
        limit = max_kb if max_kb is not None else MAX_FILE_SIZE_KB * 10  # more generous for search
        if size_kb > limit:
            return {"error": f"File is {size_kb:.1f} KB, exceeds {limit} KB limit. Pass a larger max_kb to override."}

        text = resolved.read_text(encoding="utf-8-sig")
        lines = text.splitlines()
        lower_query = query.lower()

        matches = []
        for i, line in enumerate(lines):
            if lower_query in line.lower():
                entry = {"line_number": i + 1, "content": line}
                if context_lines > 0:
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    entry["context"] = lines[start:end]
                matches.append(entry)
                if len(matches) >= max_results:
                    break

        return {
            "path": path,
            "query": query,
            "match_count": len(matches),
            "truncated": len(matches) >= max_results,
            "matches": matches,
        }

    except UnicodeDecodeError:
        return {"error": f"'{path}' is not a text file or uses an unsupported encoding"}
    except Exception as e:
        return {"error": f"Unexpected error searching '{path}': {e}"}
