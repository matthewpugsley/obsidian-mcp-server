---
status: active
title: Context Index
updated: '2026-06-09'
---

## Summary
Master index of the Obsidian vault. Claude reads this first every session to
understand what exists and what is relevant before deciding what else to load.

## How to Use This Index
- Files marked `status: active` are loaded automatically by `read_active_context`
- Files marked `status: draft` exist but are not yet ready for automatic loading
- Files with no frontmatter have not been processed yet
- Load specific files on demand with `read_context_file`

## Active Files
These files have `status: active` and will load automatically when relevant.

### _ClaudeWorkflow
- `_ClaudeWorkflow/_index.md` - index for Claude
- `_ClaudeWorkflow/mcp-state-yyyy-mm-dd.md` — most recent MCP server state snapshot written by Claude Code
- `_ClaudeWorkflow/Frontmatter Guide.md` — field reference for vault frontmatter conventions
- `_ClaudeWorkflow/Frontmatter Template.md` — Obsidian template for new vault files


## Draft Files
These files have frontmatter but are not yet active.

- Empty List

## Unprocessed Files
These files exist but have no frontmatter yet. Add frontmatter as topics come up naturally.

### Projects

- Project List (as `Projects/Project Name.md`)

### Reference

- Reference List (as `Reference/Topic A.md`)

## Notes for Claude

- Vault root: `filepath`
- Only rename or move files from within Obsidian to preserve wikilinks
- Never write to `Reference/` without explicit user confirmation
- When creating new files, add them to this index
