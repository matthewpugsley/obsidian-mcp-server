---
title: Frontmatter Guide
tags: [workflow, reference]
status: active
updated: 2025-06-09
---

## Summary
Reference guide for YAML frontmatter fields used across the vault. Defines valid
values and usage conventions for each field.

## Fields

### title
Human-readable name for the note. Can differ from the filename.
Leave blank in the template; fill in when creating a new note.

### tags
A YAML list of lowercase strings. Example: `[health, exercise, active]`
No strict controlled vocabulary yet — develop naturally as the vault grows.

### status
Controls whether Claude loads this file automatically.
Valid values:
- `draft` — work in progress, not ready for Claude to load
- `active` — currently relevant; Claude should consider loading this
- `archived` — no longer active; load only if explicitly requested

Default for new notes: `draft`

### updated
ISO date of last meaningful edit: `YYYY-MM-DD`
You update this manually; Claude updates it automatically on writes.

### priority
Optional. Used to sort active files when Claude loads context.
Valid values:
- `high` — load first
- `medium` — load second
- `low` — load last
- (blank) — treated as lower than low; sorts after all prioritized files

## Log
### 2025-05-29
- Created