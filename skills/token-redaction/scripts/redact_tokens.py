#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class PatternRule:
    name: str
    regex: re.Pattern[str]
    repl: Callable[[re.Match[str]], str]


def last4(value: str) -> str:
    return value[-4:] if len(value) >= 4 else value


def replace_prefix(match: re.Match[str]) -> str:
    prefix = match.group(1)
    token = match.group(0)
    return f"{prefix}[REDACTED:{last4(token)}]"


def replace_bearer(match: re.Match[str]) -> str:
    token = match.group(1)
    return f"Bearer [REDACTED:{last4(token)}]"


def replace_jwt(match: re.Match[str]) -> str:
    token = match.group(0)
    return f"[REDACTED_JWT:{last4(token)}]"


PATTERNS: Sequence[PatternRule] = (
    PatternRule(
        "supabase_secret",
        re.compile(r"\b(sb_secret_)[A-Za-z0-9._-]{6,}\b"),
        replace_prefix,
    ),
    PatternRule(
        "supabase_publishable",
        re.compile(r"\b(sb_publishable_)[A-Za-z0-9._-]{6,}\b"),
        replace_prefix,
    ),
    PatternRule(
        "github_pat",
        re.compile(r"\b(github_pat_)[A-Za-z0-9_]{10,}\b"),
        replace_prefix,
    ),
    PatternRule(
        "github_classic",
        re.compile(r"\b((?:ghp_|gho_|ghu_|ghs_|ghr_))[A-Za-z0-9_]{10,}\b"),
        replace_prefix,
    ),
    PatternRule(
        "slack_xox",
        re.compile(r"\b((?:xoxb-|xoxp-|xoxa-|xoxs-|xoxr-))[A-Za-z0-9-]{10,}\b"),
        replace_prefix,
    ),
    PatternRule(
        "openai_sk",
        re.compile(r"\b(sk-)[A-Za-z0-9]{10,}\b"),
        replace_prefix,
    ),
    PatternRule(
        "tank_key",
        re.compile(r"\b(tank_)[A-Za-z0-9._-]{10,}\b"),
        replace_prefix,
    ),
    PatternRule(
        "bearer",
        re.compile(r"\bBearer\s+([A-Za-z0-9._~+/-]+=*)\b"),
        replace_bearer,
    ),
    PatternRule(
        "jwt",
        re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
        replace_jwt,
    ),
)


TEXT_TYPES = ("TEXT", "CHAR", "CLOB")


def quote_ident(name: str) -> str:
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def discover_tables(conn: sqlite3.Connection) -> List[str]:
    cur = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return [row[0] for row in cur.fetchall()]


def get_columns(conn: sqlite3.Connection, table: str) -> List[Tuple[str, str, int]]:
    cur = conn.execute(f"PRAGMA table_info({quote_ident(table)})")
    return [
        (row[1], (row[2] or "").upper(), int(row[5] or 0)) for row in cur.fetchall()
    ]


def is_text_like(declared_type: str) -> bool:
    if declared_type == "":
        return True
    return any(token in declared_type for token in TEXT_TYPES)


def pick_key_columns(
    conn: sqlite3.Connection, table: str, columns: Sequence[Tuple[str, str, int]]
) -> List[str]:
    try:
        conn.execute(f"SELECT rowid FROM {quote_ident(table)} LIMIT 1")
        return ["rowid"]
    except sqlite3.Error:
        pass
    pks = [name for (name, _dtype, pk) in sorted(columns, key=lambda c: c[2]) if pk > 0]
    return pks


def redact_text(text: str, counts: Dict[str, int]) -> str:
    redacted = text
    for rule in PATTERNS:
        matches = list(rule.regex.finditer(redacted))
        if not matches:
            continue
        counts[rule.name] = counts.get(rule.name, 0) + len(matches)
        redacted = rule.regex.sub(rule.repl, redacted)
    return redacted


def scan_and_optionally_update(
    conn: sqlite3.Connection, apply: bool
) -> Dict[str, object]:
    rows_scanned = 0
    pattern_hits: Dict[str, int] = {rule.name: 0 for rule in PATTERNS}
    updated_cells = 0
    unresolved: Dict[str, int] = {}

    for table in discover_tables(conn):
        columns = get_columns(conn, table)
        text_cols = [name for (name, dtype, _pk) in columns if is_text_like(dtype)]
        if not text_cols:
            continue

        key_cols = pick_key_columns(conn, table, columns)
        if not key_cols:
            unresolved[f"{table}.__table__"] = (
                unresolved.get(f"{table}.__table__", 0) + 1
            )
            continue

        select_cols = key_cols + text_cols
        select_expr = ", ".join(
            quote_ident(c) if c != "rowid" else "rowid" for c in select_cols
        )
        cur = conn.execute(f"SELECT {select_expr} FROM {quote_ident(table)}")

        for row in cur:
            rows_scanned += 1
            row_map = dict(zip(select_cols, row))
            changed: Dict[str, str] = {}
            local_counts: Dict[str, int] = {}

            for col in text_cols:
                value = row_map.get(col)
                if not isinstance(value, str):
                    continue
                new_value = redact_text(value, local_counts)
                if new_value != value:
                    changed[col] = new_value

            if local_counts:
                for name, count in local_counts.items():
                    pattern_hits[name] = pattern_hits.get(name, 0) + count

            if changed:
                updated_cells += len(changed)
                if apply:
                    set_clause = ", ".join(
                        f"{quote_ident(c)} = ?" for c in changed.keys()
                    )
                    where_clause = " AND ".join(
                        f"{quote_ident(k)} = ?" if k != "rowid" else "rowid = ?"
                        for k in key_cols
                    )
                    values = list(changed.values()) + [row_map[k] for k in key_cols]
                    conn.execute(
                        f"UPDATE {quote_ident(table)} SET {set_clause} WHERE {where_clause}",
                        values,
                    )

    remaining = scan_remaining(conn)

    return {
        "rows_scanned": rows_scanned,
        "pattern_hits": sum(pattern_hits.values()),
        "updated_cells": updated_cells,
        "remaining_matches": remaining["total"],
        "breakdown": pattern_hits,
        "remaining_breakdown": remaining["breakdown"],
        "unresolved": unresolved,
    }


def scan_remaining(conn: sqlite3.Connection) -> Dict[str, object]:
    breakdown: Dict[str, int] = {rule.name: 0 for rule in PATTERNS}
    total = 0

    for table in discover_tables(conn):
        columns = get_columns(conn, table)
        text_cols = [name for (name, dtype, _pk) in columns if is_text_like(dtype)]
        if not text_cols:
            continue
        select_expr = ", ".join(quote_ident(c) for c in text_cols)
        cur = conn.execute(f"SELECT {select_expr} FROM {quote_ident(table)}")
        for row in cur:
            for value in row:
                if not isinstance(value, str) or not value:
                    continue
                for rule in PATTERNS:
                    count = len(rule.regex.findall(value))
                    if count:
                        breakdown[rule.name] += count
                        total += count

    return {"total": total, "breakdown": breakdown}


def build_backup_path(db_path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return db_path.with_name(f"{db_path.name}.bak.{stamp}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Redact sensitive tokens in SQLite text columns."
    )
    parser.add_argument(
        "--db",
        default="~/.local/share/opencode/opencode.db",
        help="Path to SQLite database (default: ~/.local/share/opencode/opencode.db)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply in-place updates (default is dry-run)",
    )
    parser.add_argument(
        "--delete-backup",
        action="store_true",
        help="Delete backup after successful apply",
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="Skip backup creation in apply mode"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).expanduser()

    if not db_path.exists():
        print(json.dumps({"error": f"Database not found: {db_path}"}, indent=2))
        return 1

    backup_path: Optional[Path] = None
    backup_status = "not-created"

    if args.apply and not args.no_backup:
        backup_path = build_backup_path(db_path)
        shutil.copy2(db_path, backup_path)
        backup_status = "kept"

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA busy_timeout = 5000")

    try:
        if args.apply:
            conn.execute("BEGIN IMMEDIATE")
        metrics = scan_and_optionally_update(conn, apply=args.apply)
        if args.apply:
            if metrics["remaining_matches"] != 0:
                conn.execute("ROLLBACK")
                result = {
                    "database": str(db_path),
                    "mode": "apply",
                    "status": "failed_verification",
                    "backup": {
                        "path": str(backup_path) if backup_path else None,
                        "status": backup_status,
                    },
                    **metrics,
                }
                print(json.dumps(result, indent=2))
                return 2
            conn.execute("COMMIT")
        else:
            result = {
                "database": str(db_path),
                "mode": "dry-run",
                "backup": {"path": None, "status": "not-created"},
                **metrics,
            }
            print(json.dumps(result, indent=2))
            return 0
    except sqlite3.OperationalError as exc:
        if args.apply:
            conn.execute("ROLLBACK")
        print(json.dumps({"error": f"SQLite operational error: {exc}"}, indent=2))
        return 3
    except Exception as exc:  # noqa: BLE001
        if args.apply:
            conn.execute("ROLLBACK")
        print(json.dumps({"error": str(exc)}, indent=2))
        return 4
    finally:
        conn.close()

    if args.apply and backup_path and args.delete_backup:
        backup_path.unlink(missing_ok=True)
        backup_status = "deleted"

    result = {
        "database": str(db_path),
        "mode": "apply",
        "status": "success",
        "backup": {
            "path": str(backup_path) if backup_path else None,
            "status": backup_status,
        },
        **metrics,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
