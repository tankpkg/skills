# Token Redaction

Redacts sensitive tokens in local SQLite-backed chat/session stores with a
safe, repeatable workflow: dry-run, backup, transactional update, and strict
verification.

## When To Use

Use this skill when requests include:
- "obfuscate tokens/keys in chat history"
- "sanitize local OpenCode database"
- "redact secrets from SQLite"
- "mask bearer tokens or JWTs"
- "scrub leaked API keys from local logs"

## Critical Workflow (Do Not Skip)

1. Resolve DB path and confirm file exists.
2. Run discovery scan first (read-only).
3. Create timestamped backup before any write.
4. Apply redaction in a single transaction.
5. Re-scan and fail if any targeted patterns remain.
6. Report exact metrics and backup location.
7. Delete backup only if the user explicitly asks.

Never run destructive cleanup without a verified backup unless the user
explicitly overrides safety.

## Default Target Database

- Primary: `~/.local/share/opencode/opencode.db`
- If user provides a different path, use that path.

## Redaction Patterns

Target these families by default:
- Supabase: `sb_secret_*`, `sb_publishable_*`
- GitHub: `github_pat_*`, `ghp_*`, `gho_*`, `ghu_*`, `ghs_*`, `ghr_*`
- Slack tokens: `xoxb-`, `xoxp-`, `xoxa-`, `xoxs-`, `xoxr-`
- OpenAI style: `sk-...`
- Tank keys: `tank_...`
- Authorization header values: `Bearer <token>`
- JWT-like values: `eyJ...` with 3 dot-separated segments

Keep the pattern registry configurable so new token families can be added
without rewriting the workflow.

## Masking Strategy

Use stable obfuscation for traceability without leaking value:
- Keep token family prefix.
- Keep only last 4 characters.
- Replace middle with `[REDACTED:<last4>]`.

Examples:
- `sb_secret_abc123xyz9` -> `sb_secret_[REDACTED:xyz9]`
- `Bearer abcdef123456` -> `Bearer [REDACTED:3456]`
- `eyJ...<jwt>` -> `[REDACTED_JWT:abcd]`

## SQLite Execution Model

### 1) Enumerate text-bearing columns dynamically

- Read all user tables from `sqlite_master`.
- For each table, inspect `PRAGMA table_info(table_name)`.
- Process columns typed as `TEXT`, `CHAR`, `CLOB`, or empty type in SQLite.

### 2) Discovery pass (dry-run default)

- Count candidate rows and regex matches per pattern family.
- Produce a summary before mutating data.
- In dry-run mode, do not write any changes.

### 3) Transactional write pass

- `BEGIN IMMEDIATE`.
- Update only changed cells.
- Track rows scanned, matches found, cells updated.
- `COMMIT` only after successful verification pre-checks.
- On error: `ROLLBACK`.

### 4) Verification pass

- Re-scan with strict matchers across all targeted patterns.
- If any remaining matches > 0, treat as failure.
- Report unresolved items grouped by table/column/pattern.

## Safety Controls

- Backup first, always.
- No schema edits, no table drops.
- No deletion of rows.
- Do not modify non-text columns.
- Write only when user confirms apply mode (or explicitly asks to run in-place).
- Keep backup until user asks to remove it.

## Output Contract

Return a concise audit report with:
- Database path
- Backup path and status (kept/deleted)
- Rows scanned
- Pattern hits detected
- Updated cells
- Remaining matches after verification
- Pattern family breakdown

Use this format:

```json
{
  "database": ".../opencode.db",
  "backup": {
    "path": ".../opencode.db.bak.20260220-190000",
    "status": "kept"
  },
  "rows_scanned": 0,
  "pattern_hits": 0,
  "updated_cells": 0,
  "remaining_matches": 0,
  "breakdown": {
    "github_pat": 0,
    "slack_xox": 0,
    "bearer": 0,
    "jwt": 0
  }
}
```

## Decision Rules

- If DB file is missing: stop and report exact path checked.
- If DB is locked: stop, report lock, suggest closing active app processes.
- If verification fails: do not claim success; report unresolved matches.
- If user asks "delete backup": only delete after a successful verification
  report is already produced.

## Common Mistakes To Avoid

- Updating only one known table instead of all tables.
- Scanning only one column instead of all text-like columns.
- Using only one broad regex and missing provider-specific prefixes.
- Declaring success without a strict post-redaction verification scan.
- Deleting backups before user confirmation.

## Quick Command Skeleton

Use the bundled script for deterministic local execution:

```bash
python3 scripts/redact_tokens.py --db "~/.local/share/opencode/opencode.db"
python3 scripts/redact_tokens.py --db "~/.local/share/opencode/opencode.db" --apply
python3 scripts/redact_tokens.py --db "~/.local/share/opencode/opencode.db" --apply --delete-backup
```

The script keeps dry-run as the default mode.
