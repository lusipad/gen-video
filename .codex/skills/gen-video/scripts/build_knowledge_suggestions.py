#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
STATUS_JSON_PATH = KNOWLEDGE_DIR / "status.json"
CANDIDATES_JSON_PATH = KNOWLEDGE_DIR / "candidates.json"
QUERY_LOG_PATH = KNOWLEDGE_DIR / "query-log.json"
SOURCE_REGISTRY_PATH = KNOWLEDGE_DIR / "source-registry.json"
DISCOVERY_REGISTRY_PATH = KNOWLEDGE_DIR / "discovery-registry.json"
ISSUE_INBOX_JSON_PATH = KNOWLEDGE_DIR / "issue-inbox.json"
NIGHTLY_REVIEW_JSON_PATH = KNOWLEDGE_DIR / "nightly-review.json"
SUGGESTIONS_MD_PATH = KNOWLEDGE_DIR / "suggestions.md"
SUGGESTIONS_JSON_PATH = KNOWLEDGE_DIR / "suggestions.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"

AUTO_BLOCK_START = "<!-- AUTO:SUGGESTIONS:START -->"
AUTO_BLOCK_END = "<!-- AUTO:SUGGESTIONS:END -->"
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Suggestion:
    suggestion_id: str
    priority: str
    kind: str
    title: str
    reason: str
    update_targets: list[str]
    evidence: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a prioritized knowledge update suggestion queue."
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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relpath_from_knowledge(target: str) -> str:
    return Path(os.path.relpath(SKILL_DIR / target, KNOWLEDGE_DIR)).as_posix()


def render_targets(targets: list[str]) -> str:
    if not targets:
        return "`n/a`"
    rendered: list[str] = []
    for target in targets:
        if target.startswith(("http://", "https://")):
            rendered.append(target)
            continue
        resolved = SKILL_DIR / target
        if resolved.exists():
            rendered.append(f"[`{target}`]({relpath_from_knowledge(target)})")
        else:
            rendered.append(f"`{target}`")
    return ", ".join(rendered)


def build_suggestions() -> list[Suggestion]:
    status = load_json(STATUS_JSON_PATH)
    candidates = load_json(CANDIDATES_JSON_PATH)
    query_log = load_json(QUERY_LOG_PATH)
    source_registry = load_json(SOURCE_REGISTRY_PATH)
    discovery_registry = load_json(DISCOVERY_REGISTRY_PATH)
    issue_inbox = load_json(ISSUE_INBOX_JSON_PATH) if ISSUE_INBOX_JSON_PATH.exists() else {"issues": []}
    nightly_review = load_json(NIGHTLY_REVIEW_JSON_PATH) if NIGHTLY_REVIEW_JSON_PATH.exists() else {"items": []}

    registry_map = {
        entry["id"]: entry
        for entry in source_registry.get("tracked_sources", [])
        if isinstance(entry, dict) and "id" in entry
    }
    tracked_urls = {
        str(entry.get("url", "")).strip()
        for entry in source_registry.get("tracked_sources", [])
        if entry.get("url")
    }
    candidate_urls = {
        str(entry.get("url", "")).strip()
        for entry in candidates.get("candidates", [])
        if entry.get("url")
    }

    suggestions: list[Suggestion] = []

    for source in status.get("sources", []):
        reasons: list[str] = []
        if source.get("review_state") == "overdue":
            reasons.append("review is overdue")
        elif source.get("review_state") == "due-soon":
            reasons.append("review is due soon")
        if source.get("metadata_changed"):
            reasons.append("upstream metadata changed")
        if source.get("compiled_target_missing"):
            reasons.append("compiled targets are missing")
        if not reasons:
            continue

        registry_entry = registry_map.get(source["id"], {})
        targets = list(registry_entry.get("compiled_into", []))
        targets.append("knowledge/log.md")
        priority = (
            "high"
            if source.get("review_state") == "overdue"
            or source.get("metadata_changed")
            or source.get("compiled_target_missing")
            else "medium"
        )
        evidence = ["knowledge/status.md"]
        if source.get("source_card"):
            evidence.append(f"knowledge/{source['source_card']}")
        if source.get("capture_path"):
            evidence.append(f"knowledge/{source['capture_path']}")
        suggestions.append(
            Suggestion(
                suggestion_id=f"review-{source['id']}",
                priority=priority,
                kind="tracked-source-review",
                title=f"Review tracked source `{source['id']}`",
                reason="; ".join(reasons),
                update_targets=dedupe_targets(targets),
                evidence=dedupe_targets(evidence),
            )
        )

    for item in candidates.get("candidates", []):
        if str(item.get("title", "")).startswith("watchlist fetch failed:"):
            suggestions.append(
                Suggestion(
                    suggestion_id=f"repair-watchlist-{item['watch_id']}",
                    priority="high",
                    kind="watchlist-repair",
                    title=f"Repair discovery watchlist `{item['watch_id']}`",
                    reason=item["title"],
                    update_targets=["knowledge/discovery-registry.json", "knowledge/log.md"],
                    evidence=["knowledge/candidates.md"],
                )
            )
            continue
        promote_targets = ["knowledge/source-registry.json", *item.get("promote_into", [])]
        suggestions.append(
            Suggestion(
                suggestion_id=f"candidate-{item['watch_id']}-{slugify(item['title'])}",
                priority="medium" if item.get("owner_type") == "official" else "low",
                kind="candidate-promotion",
                title=f"Review discovery candidate: {item['title']}",
                reason=(
                    f"untracked {item.get('owner_type', 'unknown')} candidate from `{item['watch_id']}` "
                    f"matched {', '.join(item.get('matched_keywords', [])) or 'watch keywords'}"
                ),
                update_targets=dedupe_targets(promote_targets),
                evidence=["knowledge/candidates.md"],
            )
        )

    for entry in query_log.get("queries", []):
        if entry.get("status") == "pending":
            priority = entry.get("importance", "medium")
            suggestions.append(
                Suggestion(
                    suggestion_id=f"query-{entry['id']}",
                    priority=priority if priority in PRIORITY_ORDER else "medium",
                    kind="query-writeback",
                    title=f"Write back recurring question `{entry['id']}`",
                    reason="high-value user question is still pending distillation into persistent knowledge",
                    update_targets=dedupe_targets(entry.get("promote_into", []) or ["knowledge/wiki/README.md"]),
                    evidence=["knowledge/query-log.json"],
                )
            )
        elif entry.get("status") == "resolved":
            missing_resolutions = [
                target for target in entry.get("resolved_by", []) if not (SKILL_DIR / target).exists()
            ]
            if missing_resolutions:
                suggestions.append(
                    Suggestion(
                        suggestion_id=f"repair-query-{entry['id']}",
                        priority="high",
                        kind="query-resolution-repair",
                        title=f"Repair resolved query targets for `{entry['id']}`",
                        reason="query is marked resolved but one or more resolved targets are missing",
                        update_targets=dedupe_targets(entry.get("resolved_by", []) + entry.get("promote_into", [])),
                        evidence=["knowledge/query-log.json"],
                    )
                )

    blogger_watchlists = [
        watch
        for watch in discovery_registry.get("watchlists", [])
        if watch.get("owner_type") == "blogger"
    ]
    blogger_candidates = candidates.get("summary", {}).get("blogger_candidates", 0)
    if blogger_watchlists and blogger_candidates == 0:
        suggestions.append(
            Suggestion(
                suggestion_id="blogger-discovery-gap",
                priority="high",
                kind="discovery-gap",
                title="Strengthen blogger discovery coverage",
                reason="blogger watchlists exist, but the latest discovery run surfaced 0 blogger candidates",
                update_targets=[
                    "knowledge/discovery-registry.json",
                    "knowledge/wiki/concepts/karpathy-gap-analysis.md",
                    "knowledge/log.md",
                ],
                evidence=["knowledge/candidates.md", "knowledge/discovery-registry.json"],
            )
        )

    for issue in issue_inbox.get("issues", []):
        urls = [
            preview.get("final_url") or preview.get("url")
            for preview in issue.get("source_previews", [])
            if preview.get("url")
        ]
        unseen_urls = [
            url
            for url in urls
            if url not in tracked_urls and url not in candidate_urls
        ]
        if not unseen_urls:
            continue
        issue_ref = f"{issue.get('repository', '?')}#{issue.get('number', '?')}"
        suggestions.append(
            Suggestion(
                suggestion_id=f"issue-inbox-{issue.get('repository', 'repo').replace('/', '-')}-{issue.get('number', '0')}",
                priority="high",
                kind="issue-inbox-review",
                title=f"Review issue inbox sources from `{issue_ref}`",
                reason=f"bookmarked issue was ingested and still contains {len(unseen_urls)} URLs not present in tracked sources or discovery candidates",
                update_targets=[
                    "knowledge/source-registry.json",
                    "knowledge/log.md",
                ],
                evidence=[
                    "knowledge/issue-inbox.md",
                    issue.get("html_url", "knowledge/issue-inbox.md"),
                ],
            )
        )

    for item in nightly_review.get("items", []):
        if item.get("known_state") != "new":
            continue
        suggestions.append(
            Suggestion(
                suggestion_id=f"nightly-{item.get('source_id', 'source')}-{slugify(item.get('title', 'item'))}",
                priority="high" if item.get("owner_type") == "creator" else "medium",
                kind="nightly-review",
                title=f"Review nightly intelligence item: {item.get('title', 'Untitled')}",
                reason=(
                    f"nightly review surfaced a new {item.get('owner_type', 'unknown')} item from "
                    f"`{item.get('source_title', item.get('source_id', 'source'))}`"
                ),
                update_targets=dedupe_targets(item.get("review_into", []) + ["knowledge/source-registry.json"]),
                evidence=[
                    "knowledge/nightly-review.md",
                    item.get("url", "knowledge/nightly-review.md"),
                ],
            )
        )

    suggestions.sort(
        key=lambda item: (
            PRIORITY_ORDER[item.priority],
            item.kind,
            item.title.lower(),
        )
    )
    return suggestions


def dedupe_targets(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def slugify(text: str) -> str:
    chars = []
    for char in text.lower():
        if char.isalnum():
            chars.append(char)
        elif char in {" ", "-", "_"}:
            chars.append("-")
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:48] or "item"


def build_payload(suggestions: list[Suggestion]) -> dict[str, Any]:
    summary = {
        "total": len(suggestions),
        "high": sum(1 for item in suggestions if item.priority == "high"),
        "medium": sum(1 for item in suggestions if item.priority == "medium"),
        "low": sum(1 for item in suggestions if item.priority == "low"),
    }
    return {
        "summary": summary,
        "suggestions": [
            {
                "id": item.suggestion_id,
                "priority": item.priority,
                "kind": item.kind,
                "title": item.title,
                "reason": item.reason,
                "update_targets": item.update_targets,
                "evidence": item.evidence,
            }
            for item in suggestions
        ],
    }


def render_markdown(suggestions: list[Suggestion]) -> str:
    lines = [
        "# Knowledge Suggestions",
        "",
        "Generated from `status.json`, `candidates.json`, `issue-inbox.json`, `nightly-review.json`, `query-log.json`, and discovery/source registries by `scripts/build_knowledge_suggestions.py`.",
        "",
    ]
    if not suggestions:
        lines.extend(["- No actionable knowledge suggestions in the latest run.", ""])
        return "\n".join(lines)

    for priority in ("high", "medium", "low"):
        group = [item for item in suggestions if item.priority == priority]
        lines.extend([f"## {priority.title()} Priority", ""])
        if not group:
            lines.append("- None.")
            lines.append("")
            continue
        for item in group:
            lines.extend(
                [
                    f"### {item.title}",
                    "",
                    f"- kind: `{item.kind}`",
                    f"- reason: {item.reason}",
                    f"- update_targets: {render_targets(item.update_targets)}",
                    f"- evidence: {render_targets(item.evidence)}",
                    "",
                ]
            )
    return "\n".join(lines)


def truncate(text: str, limit: int = 80) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_index_block(suggestions: list[Suggestion]) -> str:
    lines = [
        AUTO_BLOCK_START,
        f"- [suggestions.md](suggestions.md) contains {len(suggestions)} actionable update suggestions.",
        f"- High priority items: {sum(1 for item in suggestions if item.priority == 'high')}",
    ]
    for item in suggestions[:3]:
        lines.append(f"  - `{item.priority}` -> {truncate(item.title, 68)}")
    lines.append(AUTO_BLOCK_END)
    return "\n".join(lines)


def update_index(suggestions: list[Suggestion], check: bool) -> bool:
    current = INDEX_PATH.read_text(encoding="utf-8")
    block = build_index_block(suggestions)
    if AUTO_BLOCK_START in current and AUTO_BLOCK_END in current:
        before, remainder = current.split(AUTO_BLOCK_START, 1)
        _, after = remainder.split(AUTO_BLOCK_END, 1)
        updated = before.rstrip() + "\n\n" + block + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    return write_text_if_changed(INDEX_PATH, updated, check)


def main() -> int:
    args = parse_args()
    suggestions = build_suggestions()
    payload = build_payload(suggestions)
    write_json_if_changed(SUGGESTIONS_JSON_PATH, payload, args.check)
    write_text_if_changed(SUGGESTIONS_MD_PATH, render_markdown(suggestions), args.check)
    update_index(suggestions, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
