#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib import error, request


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
RAW_SOURCES_DIR = KNOWLEDGE_DIR / "raw" / "sources"
RAW_CAPTURE_METADATA_DIR = KNOWLEDGE_DIR / "raw" / "captures" / "http-metadata"
REGISTRY_PATH = KNOWLEDGE_DIR / "source-registry.json"
STATUS_MD_PATH = KNOWLEDGE_DIR / "status.md"
STATUS_JSON_PATH = KNOWLEDGE_DIR / "status.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"

AUTO_BLOCK_START = "<!-- AUTO:STATUS:START -->"
AUTO_BLOCK_END = "<!-- AUTO:STATUS:END -->"
USER_AGENT = "gen-video-knowledge-refresh/1.0"
HTTP_TIMEOUT_SECONDS = 20
SIGNIFICANT_HTTP_HEADERS = [
    "content-length",
    "content-type",
    "etag",
    "last-modified",
    "cache-control",
]
COMPARISON_HTTP_HEADERS = [
    "content-type",
    "last-modified",
]
REQUIRED_KEYS = [
    "id",
    "title",
    "author",
    "url",
    "source_type",
    "captured_at",
    "published_at",
    "volatility",
    "scope",
    "status",
    "review_every_days",
    "last_reviewed_at",
    "compiled_into",
    "capture",
]


@dataclass
class SourceState:
    entry: dict[str, Any]
    card_path: Path
    capture_path: Path | None
    due_date: date
    review_state: str
    metadata_changed: bool
    metadata_ok: bool
    compiled_target_missing: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh the gen-video knowledge registry, status pages, and source cards."
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip remote metadata fetches and only refresh local derived files.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate registry and generated files without writing changes.",
    )
    return parser.parse_args()


def escape_yaml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def load_registry() -> list[dict[str, Any]]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    tracked_sources = payload.get("tracked_sources")
    if not isinstance(tracked_sources, list):
        raise ValueError("source-registry.json must contain a tracked_sources array")
    return tracked_sources


def validate_entry(entry: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_KEYS if key not in entry]
    if missing:
        raise ValueError(f"source {entry.get('id', '<unknown>')} is missing keys: {missing}")
    if not isinstance(entry["compiled_into"], list):
        raise ValueError(f"source {entry['id']} compiled_into must be a list")
    if not isinstance(entry["capture"], dict):
        raise ValueError(f"source {entry['id']} capture must be an object")
    if entry["capture"].get("mode") != "http-metadata":
        raise ValueError(f"source {entry['id']} capture.mode must be http-metadata")
    if int(entry["review_every_days"]) <= 0:
        raise ValueError(f"source {entry['id']} review_every_days must be > 0")
    date.fromisoformat(entry["captured_at"])
    if entry["published_at"]:
        date.fromisoformat(entry["published_at"])
    date.fromisoformat(entry["last_reviewed_at"])


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


def existing_source_card_path(source_id: str) -> Path | None:
    matches = sorted(RAW_SOURCES_DIR.glob(f"*_{source_id}.source.md"))
    if matches:
        return matches[-1]
    return None


def render_source_card(entry: dict[str, Any]) -> str:
    compiled_lines = "\n".join(
        f"- `{target}`" for target in entry["compiled_into"]
    ) or "- none"
    return f"""---
title: "{escape_yaml(entry["title"])}"
author: "{escape_yaml(entry["author"])}"
url: "{escape_yaml(entry["url"])}"
source_type: "{escape_yaml(entry["source_type"])}"
captured_at: {entry["captured_at"]}
published_at: "{escape_yaml(entry["published_at"])}"
volatility: "{escape_yaml(entry["volatility"])}"
scope: "{escape_yaml(entry["scope"])}"
status: "{escape_yaml(entry["status"])}"
---

Canonical source record managed from `knowledge/source-registry.json`.

Tracking:

- review_every_days: {entry["review_every_days"]}
- last_reviewed_at: {entry["last_reviewed_at"]}

Compiled into:

{compiled_lines}
"""


def ensure_source_card(entry: dict[str, Any], check: bool) -> Path:
    current = existing_source_card_path(entry["id"])
    target = current or (RAW_SOURCES_DIR / f'{entry["captured_at"]}_{entry["id"]}.source.md')
    write_text_if_changed(target, render_source_card(entry), check)
    return target


def fetch_http_metadata(url: str) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT}
    attempts = [
        request.Request(url, headers=headers, method="HEAD"),
        request.Request(url, headers=headers, method="GET"),
    ]
    last_exception: Exception | None = None
    for req in attempts:
        try:
            with request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as response:
                normalized_headers = {
                    key.lower(): value
                    for key, value in response.headers.items()
                    if key.lower() in SIGNIFICANT_HTTP_HEADERS
                }
                return {
                    "status": getattr(response, "status", response.getcode()),
                    "final_url": response.geturl(),
                    "headers": normalized_headers,
                }
        except error.HTTPError as exc:
            if exc.code in {400, 403, 405, 429, 500, 502, 503, 504} and req.get_method() == "HEAD":
                last_exception = exc
                continue
            return {
                "status": exc.code,
                "final_url": url,
                "headers": {},
                "error": exc.reason,
            }
        except Exception as exc:  # noqa: BLE001
            last_exception = exc
            if req.get_method() == "HEAD":
                continue
            break
    if last_exception is None:
        raise RuntimeError(f"unable to fetch metadata for {url}")
    return {
        "status": "unreachable",
        "final_url": url,
        "headers": {},
        "error": str(last_exception),
    }


def capture_path_for(source_id: str) -> Path:
    return RAW_CAPTURE_METADATA_DIR / f"{source_id}.json"


def canonicalize_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    headers = payload.get("headers", {})
    stable_headers = {
        key: headers[key]
        for key in COMPARISON_HTTP_HEADERS
        if key in headers
    }
    stable_payload = {
        "status": payload.get("status"),
        "final_url": payload.get("final_url"),
        "headers": stable_headers,
    }
    if "error" in payload:
        stable_payload["error"] = payload["error"]
    return stable_payload


def metadata_changed(path: Path, payload: dict[str, Any]) -> bool:
    if not path.exists():
        return True
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True
    return canonicalize_metadata(existing) != canonicalize_metadata(payload)


def review_state_for(due_date: date) -> str:
    delta = (due_date - date.today()).days
    if delta < 0:
        return "overdue"
    if delta <= 3:
        return "due-soon"
    return "healthy"


def compiled_target_missing(entry: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for target in entry["compiled_into"]:
        target_path = SKILL_DIR / target
        if not target_path.exists():
            missing.append(target)
    return missing


def build_status(states: list[SourceState]) -> tuple[dict[str, Any], str]:
    grouped: dict[str, list[SourceState]] = {
        "overdue": [],
        "due-soon": [],
        "healthy": [],
    }
    for state in states:
        grouped[state.review_state].append(state)

    changed = [state for state in states if state.metadata_changed]
    missing_targets = [state for state in states if state.compiled_target_missing]

    payload = {
        "summary": {
            "overdue": len(grouped["overdue"]),
            "due_soon": len(grouped["due-soon"]),
            "healthy": len(grouped["healthy"]),
            "metadata_changed": len(changed),
            "compiled_target_missing": len(missing_targets),
        },
        "sources": [
            {
                "id": state.entry["id"],
                "scope": state.entry["scope"],
                "volatility": state.entry["volatility"],
                "due_date": state.due_date.isoformat(),
                "review_state": state.review_state,
                "metadata_changed": state.metadata_changed,
                "metadata_ok": state.metadata_ok,
                "source_card": state.card_path.relative_to(KNOWLEDGE_DIR).as_posix(),
                "capture_path": state.capture_path.relative_to(KNOWLEDGE_DIR).as_posix()
                if state.capture_path
                else None,
                "compiled_target_missing": state.compiled_target_missing,
            }
            for state in states
        ],
    }

    lines: list[str] = [
        "# Knowledge Status",
        "",
        "Generated from `source-registry.json` by `scripts/refresh_knowledge.py`.",
        "",
        "## Review Summary",
        "",
        f'- `overdue`: {len(grouped["overdue"])}',
        f'- `due-soon`: {len(grouped["due-soon"])}',
        f'- `healthy`: {len(grouped["healthy"])}',
        "",
        "## Upstream Change Watch",
        "",
    ]
    if changed:
        for state in changed:
            lines.append(
                f'- `{state.entry["id"]}` changed upstream or has new metadata; see '
                f'[`{state.capture_path.relative_to(KNOWLEDGE_DIR).as_posix()}`]'
                f'({state.capture_path.relative_to(KNOWLEDGE_DIR).as_posix()}).'
            )
    else:
        lines.append("- No upstream metadata changes detected in the latest refresh.")

    lines.extend(["", "## Tracked Sources", "", "| ID | Scope | Volatility | Due | State | Source Card | Capture |", "| --- | --- | --- | --- | --- | --- | --- |"])
    for state in states:
        capture_label = (
            f'[`{state.capture_path.relative_to(KNOWLEDGE_DIR).as_posix()}`]'
            f'({state.capture_path.relative_to(KNOWLEDGE_DIR).as_posix()})'
            if state.capture_path
            else "n/a"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    f'`{state.entry["id"]}`',
                    state.entry["scope"],
                    state.entry["volatility"],
                    state.due_date.isoformat(),
                    state.review_state,
                    f'[`{state.card_path.relative_to(KNOWLEDGE_DIR).as_posix()}`]'
                    f'({state.card_path.relative_to(KNOWLEDGE_DIR).as_posix()})',
                    capture_label,
                ]
            )
            + " |"
        )

    lines.extend(["", "## Missing Compiled Targets", ""])
    if missing_targets:
        for state in missing_targets:
            targets = ", ".join(f"`{target}`" for target in state.compiled_target_missing)
            lines.append(f'- `{state.entry["id"]}` -> {targets}')
    else:
        lines.append("- None.")

    return payload, "\n".join(lines) + "\n"


def build_index_block(states: list[SourceState]) -> str:
    overdue = [state for state in states if state.review_state == "overdue"]
    due_soon = [state for state in states if state.review_state == "due-soon"]
    changed = [state for state in states if state.metadata_changed]

    lines = [
        AUTO_BLOCK_START,
        "- [status.md](status.md) is the CI-generated watchlist for review cadence and upstream metadata changes.",
        f"- Overdue reviews: {len(overdue)}",
    ]
    if overdue:
        lines.extend(
            f"  - `{state.entry['id']}` due {state.due_date.isoformat()}" for state in overdue
        )
    lines.append(f"- Due soon: {len(due_soon)}")
    if due_soon:
        lines.extend(
            f"  - `{state.entry['id']}` due {state.due_date.isoformat()}" for state in due_soon
        )
    lines.append(f"- Upstream metadata changes detected: {len(changed)}")
    if changed:
        lines.extend(f"  - `{state.entry['id']}`" for state in changed)
    lines.append(AUTO_BLOCK_END)
    return "\n".join(lines)


def update_index(states: list[SourceState], check: bool) -> bool:
    current = INDEX_PATH.read_text(encoding="utf-8")
    block = build_index_block(states)
    if AUTO_BLOCK_START in current and AUTO_BLOCK_END in current:
        before, remainder = current.split(AUTO_BLOCK_START, 1)
        _, after = remainder.split(AUTO_BLOCK_END, 1)
        updated = before.rstrip() + "\n\n" + block + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    return write_text_if_changed(INDEX_PATH, updated, check)


def main() -> int:
    args = parse_args()
    entries = load_registry()
    states: list[SourceState] = []
    wrote_any = False

    for entry in entries:
        validate_entry(entry)
        card_path = ensure_source_card(entry, args.check)
        due = date.fromisoformat(entry["last_reviewed_at"]) + timedelta(days=int(entry["review_every_days"]))
        capture_path: Path | None = None
        changed = False
        metadata_ok = True
        if not args.no_fetch:
            capture_path = capture_path_for(entry["id"])
            payload = fetch_http_metadata(entry["url"])
            changed = metadata_changed(capture_path, payload)
            if changed:
                wrote_any = write_json_if_changed(capture_path, payload, args.check) or wrote_any
            metadata_ok = payload.get("status") != "unreachable"
        missing = compiled_target_missing(entry)
        states.append(
            SourceState(
                entry=entry,
                card_path=card_path,
                capture_path=capture_path if capture_path and capture_path.exists() else capture_path,
                due_date=due,
                review_state=review_state_for(due),
                metadata_changed=changed,
                metadata_ok=metadata_ok,
                compiled_target_missing=missing,
            )
        )

    states.sort(key=lambda item: (item.review_state, item.due_date.isoformat(), item.entry["id"]))
    status_payload, status_markdown = build_status(states)
    wrote_any = write_json_if_changed(STATUS_JSON_PATH, status_payload, args.check) or wrote_any
    wrote_any = write_text_if_changed(STATUS_MD_PATH, status_markdown, args.check) or wrote_any
    wrote_any = update_index(states, args.check) or wrote_any

    if args.check:
        return 0
    return 0 if wrote_any or not args.no_fetch else 0


if __name__ == "__main__":
    raise SystemExit(main())
