#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
QUERY_LOG_PATH = KNOWLEDGE_DIR / "query-log.json"
WRITEBACK_MD_PATH = KNOWLEDGE_DIR / "writeback-queue.md"
WRITEBACK_JSON_PATH = KNOWLEDGE_DIR / "writeback-queue.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"

AUTO_BLOCK_START = "<!-- AUTO:WRITEBACK:START -->"
AUTO_BLOCK_END = "<!-- AUTO:WRITEBACK:END -->"
REQUIRED_KEYS = [
    "id",
    "asked_at",
    "source",
    "question",
    "importance",
    "status",
    "resolved_by",
    "promote_into",
    "tags",
    "notes",
]
IMPORTANCE_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class QueryRecord:
    entry: dict[str, Any]
    missing_resolutions: list[str]
    missing_promote_targets: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a query-derived knowledge writeback queue."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate generated files without writing updates.",
    )
    return parser.parse_args()


def write_text_if_changed(path: Path, content: str, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return False
    if check:
        raise RuntimeError(f"{path} is out of date")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def write_json_if_changed(path: Path, payload: Any, check: bool) -> bool:
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return write_text_if_changed(path, content, check)


def load_query_log() -> list[dict[str, Any]]:
    payload = json.loads(QUERY_LOG_PATH.read_text(encoding="utf-8"))
    queries = payload.get("queries")
    if not isinstance(queries, list):
        raise ValueError("query-log.json must contain a queries array")
    return queries


def validate_query(entry: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_KEYS if key not in entry]
    if missing:
        raise ValueError(f"query {entry.get('id', '<unknown>')} is missing keys: {missing}")
    date.fromisoformat(entry["asked_at"])
    if entry["importance"] not in IMPORTANCE_ORDER:
        raise ValueError(f"query {entry['id']} has invalid importance: {entry['importance']}")
    if entry["status"] not in {"pending", "resolved"}:
        raise ValueError(f"query {entry['id']} has invalid status: {entry['status']}")
    for key in ("resolved_by", "promote_into", "tags"):
        if not isinstance(entry[key], list):
            raise ValueError(f"query {entry['id']} field {key} must be a list")


def target_exists(target: str) -> bool:
    return (SKILL_DIR / target).exists()


def relpath_from_knowledge(target: str) -> str:
    return Path(os.path.relpath(SKILL_DIR / target, KNOWLEDGE_DIR)).as_posix()


def link_targets(targets: list[str]) -> str:
    if not targets:
        return "`n/a`"
    rendered: list[str] = []
    for target in targets:
        resolved = SKILL_DIR / target
        if resolved.exists():
            rendered.append(f"[`{target}`]({relpath_from_knowledge(target)})")
        else:
            rendered.append(f"`{target}`")
    return ", ".join(rendered)


def classify_queries(entries: list[dict[str, Any]]) -> list[QueryRecord]:
    records: list[QueryRecord] = []
    for entry in entries:
        validate_query(entry)
        missing_resolutions = [target for target in entry["resolved_by"] if not target_exists(target)]
        missing_promote_targets = [target for target in entry["promote_into"] if not target_exists(target)]
        records.append(
            QueryRecord(
                entry=entry,
                missing_resolutions=missing_resolutions,
                missing_promote_targets=missing_promote_targets,
            )
        )
    records.sort(
        key=lambda item: (
            0 if item.entry["status"] == "pending" else 1,
            IMPORTANCE_ORDER[item.entry["importance"]],
            item.entry["asked_at"],
            item.entry["id"],
        )
    )
    return records


def build_payload(records: list[QueryRecord]) -> dict[str, Any]:
    pending = [record for record in records if record.entry["status"] == "pending"]
    resolved = [record for record in records if record.entry["status"] == "resolved"]
    broken_resolutions = [
        record for record in records if record.entry["status"] == "resolved" and record.missing_resolutions
    ]
    broken_promote_targets = [record for record in records if record.missing_promote_targets]
    action_items = [
        record
        for record in records
        if record.entry["status"] == "pending"
        or record.missing_resolutions
        or record.missing_promote_targets
    ]
    return {
        "summary": {
            "total_queries": len(records),
            "pending_queries": len(pending),
            "resolved_queries": len(resolved),
            "broken_resolution_links": len(broken_resolutions),
            "broken_promote_targets": len(broken_promote_targets),
            "action_items": len(action_items),
        },
        "queries": [
            {
                "id": record.entry["id"],
                "asked_at": record.entry["asked_at"],
                "importance": record.entry["importance"],
                "status": record.entry["status"],
                "source": record.entry["source"],
                "question": record.entry["question"],
                "tags": record.entry["tags"],
                "notes": record.entry["notes"],
                "resolved_by": record.entry["resolved_by"],
                "promote_into": record.entry["promote_into"],
                "missing_resolutions": record.missing_resolutions,
                "missing_promote_targets": record.missing_promote_targets,
            }
            for record in records
        ],
    }


def render_markdown(records: list[QueryRecord]) -> str:
    action_items = [
        record
        for record in records
        if record.entry["status"] == "pending"
        or record.missing_resolutions
        or record.missing_promote_targets
    ]
    resolved = [
        record
        for record in records
        if record.entry["status"] == "resolved"
        and not record.missing_resolutions
        and not record.missing_promote_targets
    ]

    lines = [
        "# Query Writeback Queue",
        "",
        "Generated from `query-log.json` by `scripts/build_query_writeback_queue.py`.",
        "",
        "## Action Queue",
        "",
    ]
    if action_items:
        for record in action_items:
            actions: list[str] = []
            if record.entry["status"] == "pending":
                actions.append("distill this recurring question into wiki guidance")
            if record.missing_resolutions:
                actions.append("repair missing resolved targets")
            if record.missing_promote_targets:
                actions.append("repair missing promote targets")
            lines.extend(
                [
                    f"### {record.entry['id']}",
                    "",
                    f"- importance: `{record.entry['importance']}`",
                    f"- status: `{record.entry['status']}`",
                    f"- source: `{record.entry['source']}`",
                    f"- question: {record.entry['question']}",
                    f"- next_action: {'; '.join(actions)}",
                    f"- promote_into: {link_targets(record.entry['promote_into'])}",
                    f"- resolved_by: {link_targets(record.entry['resolved_by'])}",
                    f"- tags: {', '.join(f'`{tag}`' for tag in record.entry['tags']) or '`n/a`'}",
                    f"- notes: {record.entry['notes']}",
                    "",
                ]
            )
            if record.missing_resolutions:
                lines.append(
                    f"- missing_resolutions: {', '.join(f'`{target}`' for target in record.missing_resolutions)}"
                )
                lines.append("")
            if record.missing_promote_targets:
                lines.append(
                    "- missing_promote_targets: "
                    + ", ".join(f"`{target}`" for target in record.missing_promote_targets)
                )
                lines.append("")
    else:
        lines.append("- No pending query writeback actions in the latest run.")
        lines.append("")

    lines.extend(["## Resolved Questions", ""])
    if resolved:
        for record in resolved:
            lines.extend(
                [
                    f"- `{record.entry['id']}` -> {record.entry['question']}",
                    f"  resolved_by: {link_targets(record.entry['resolved_by'])}",
                ]
            )
    else:
        lines.append("- No resolved query entries yet.")
    lines.append("")
    return "\n".join(lines)


def truncate(text: str, limit: int = 88) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_index_block(records: list[QueryRecord]) -> str:
    action_items = [
        record
        for record in records
        if record.entry["status"] == "pending"
        or record.missing_resolutions
        or record.missing_promote_targets
    ]
    lines = [
        AUTO_BLOCK_START,
        f"- [writeback-queue.md](writeback-queue.md) contains {len(action_items)} query-derived follow-up items.",
    ]
    for record in action_items[:3]:
        lines.append(f"  - `{record.entry['id']}` -> {truncate(record.entry['question'], 72)}")
    lines.append(AUTO_BLOCK_END)
    return "\n".join(lines)


def update_index(records: list[QueryRecord], check: bool) -> bool:
    current = INDEX_PATH.read_text(encoding="utf-8")
    block = build_index_block(records)
    if AUTO_BLOCK_START in current and AUTO_BLOCK_END in current:
        before, remainder = current.split(AUTO_BLOCK_START, 1)
        _, after = remainder.split(AUTO_BLOCK_END, 1)
        updated = before.rstrip() + "\n\n" + block + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    return write_text_if_changed(INDEX_PATH, updated, check)


def main() -> int:
    args = parse_args()
    records = classify_queries(load_query_log())
    payload = build_payload(records)
    write_json_if_changed(WRITEBACK_JSON_PATH, payload, args.check)
    write_text_if_changed(WRITEBACK_MD_PATH, render_markdown(records), args.check)
    update_index(records, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
