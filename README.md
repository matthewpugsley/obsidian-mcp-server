# obsidian-mcp-server

An [MCP](https://modelcontextprotocol.io/) server that gives Claude (or any MCP-compatible AI client) read and write access to an [Obsidian](https://obsidian.md/) vault. Claude can list, read, search, and write markdown notes — letting it serve as a persistent memory and knowledge base across sessions.

## Features

- Read individual vault files, with frontmatter parsing and section filtering
- Load all `status: active` files automatically at the start of a session
- Full-text search across vault markdown files
- Read and search arbitrary text files (CSV, TSV, etc.)
- Write new files or append content to existing ones

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- [Claude Desktop](https://claude.ai/download) or another MCP-compatible client

## Setup

**1. Clone and install dependencies**

```
git clone https://github.com/matthewpugsley/obsidian-mcp-server.git
cd obsidian-mcp-server
uv sync
```

**2. Create your `.env` file**

```
copy .env.example .env
```

Edit `.env` and fill in your paths:

```
VAULT_ROOT=C:\ObsidianVaults\Main
MCP_SOURCE=C:\path\to\obsidian-mcp-server
MCP_DEST=C:\path\to\deploy\location
```

**3. Deploy**

```
.\deploy.ps1
```

This copies the server files to `MCP_DEST` and runs `uv sync` there.

**4. Configure Claude Desktop**

Add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "obsidian-mcp-server": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "C:\\path\\to\\deploy\\location",
        "python",
        "C:\\path\\to\\deploy\\location\\server.py"
      ],
      "env": {
        "VAULT_ROOT": "C:\\ObsidianVaults\\Main"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_context_files` | List vault files, optionally filtered by folder, status, or tags |
| `read_context_file` | Read a single file by vault-relative path, with optional section filtering |
| `read_active_context` | Load all `status: active` files, ordered by priority then last updated |
| `read_raw_file` | Read any file as raw text, bypassing markdown parsing |
| `search_context` | Full-text search across vault markdown files, ranked by match count |
| `search_raw_file` | Search within a single file for matching lines, with optional context |
| `write_context_file` | Create or overwrite a vault file with frontmatter and content |
| `append_to_context_file` | Append content to an existing file, optionally under a named section |

## Vault Conventions

This server works with any Obsidian vault. For best results with `read_active_context`, add YAML frontmatter to your notes:

```yaml
---
title: My Note
status: active      # active | draft | archived
priority: high      # high | medium | low (optional)
tags: [reference]
updated: 2026-01-01
---
```

See `docs/` for a suggested vault layout and frontmatter reference.

## License

MIT
