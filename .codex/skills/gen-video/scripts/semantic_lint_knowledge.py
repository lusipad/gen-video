#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
WIKI_DIR = KNOWLEDGE_DIR / "wiki"
RAW_SOURCES_DIR = KNOWLEDGE_DIR / "raw" / "sources"
SOURCE_REGISTRY_PATH = KNOWLEDGE_DIR / "source-registry.json"
DISCOVERY_REGISTRY_PATH = KNOWLEDGE_DIR / "discovery-registry.json"
QUERY_LOG_PATH = KNOWLEDGE_DIR / "query-log.json"
ISSUE_INBOX_CONFIG_PATH = KNOWLEDGE_DIR / "github-issue-inbox.json"
NIGHTLY_REVIEW_CONFIG_PATH = KNOWLEDGE_DIR / "nightly-review-registry.json"
LINT_MD_PATH = KNOWLEDGE_DIR / "lint.md"
LINT_JSON_PATH = KNOWLEDGE_DIR / "lint.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"

AUTO_BLOCK_START = "<!-- AUTO:LINT:START -->"
AUTO_BLOCK_END = "<!-- AUTO:LINT:END -->"
SOURCE_CARD_REQUIRED_KEYS = [
    "title",
    "author",
    "url",
    "source_type",
    "captured_at",
    "published_at",
    "volatility",
    "scope",
    "status",
]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    path: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run semantic lint checks against the gen-video knowledge base."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate generated lint reports without writing updates.",
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


def relpath_to_skill(path: Path) -> str:
    return path.relative_to(SKILL_DIR).as_posix()


def relpath_to_knowledge(path: Path) -> str:
    return path.relative_to(KNOWLEDGE_DIR).as_posix()


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None
    frontmatter_text = parts[0][4:]
    payload: dict[str, str] = {}
    for raw_line in frontmatter_text.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip().strip('"')
    return payload


def link_target_exists(target: str) -> bool:
    return (SKILL_DIR / target).exists()


def collect_issues() -> list[Issue]:
    issues: list[Issue] = []
    issues.extend(check_wiki_sources())
    issues.extend(check_source_cards())
    issues.extend(check_registry_targets())
    issues.extend(check_query_targets())
    issues.extend(check_issue_inbox_config())
    issues.extend(check_nightly_review_config())
    issues.extend(check_orphan_wiki_pages())
    return sorted(
        issues,
        key=lambda item: (
            0 if item.severity == "error" else 1,
            item.code,
            item.path,
        ),
    )


def check_wiki_sources() -> list[Issue]:
    issues: list[Issue] = []
    for path in sorted(WIKI_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?m)^Sources:\s*$", text) is None:
            issues.append(
                Issue(
                    severity="error",
                    code="missing-sources-section",
                    message="wiki page is missing a Sources section",
                    path=relpath_to_skill(path),
                )
            )
    return issues


def check_source_cards() -> list[Issue]:
    issues: list[Issue] = []
    for path in sorted(RAW_SOURCES_DIR.glob("*.source.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        if frontmatter is None:
            issues.append(
                Issue(
                    severity="error",
                    code="invalid-source-card-frontmatter",
                    message="source card must start with valid YAML frontmatter",
                    path=relpath_to_skill(path),
                )
            )
            continue
        missing = [key for key in SOURCE_CARD_REQUIRED_KEYS if key not in frontmatter]
        if missing:
            issues.append(
                Issue(
                    severity="error",
                    code="missing-source-card-field",
                    message=f"source card frontmatter is missing keys: {missing}",
                    path=relpath_to_skill(path),
                )
            )
    return issues


def check_registry_targets() -> list[Issue]:
    issues: list[Issue] = []
    source_registry = load_json(SOURCE_REGISTRY_PATH).get("tracked_sources", [])
    for entry in source_registry:
        targets = entry.get("compiled_into", [])
        if not isinstance(targets, list):
            issues.append(
                Issue(
                    severity="error",
                    code="compiled-into-not-list",
                    message=f"source {entry.get('id', '<unknown>')} compiled_into must be a list",
                    path=relpath_to_skill(SOURCE_REGISTRY_PATH),
                )
            )
            continue
        if not targets:
            issues.append(
                Issue(
                    severity="warning",
                    code="empty-compiled-into",
                    message=f"source {entry['id']} has no compiled targets",
                    path=relpath_to_skill(SOURCE_REGISTRY_PATH),
                )
            )
        for target in targets:
            if not link_target_exists(target):
                issues.append(
                    Issue(
                        severity="error",
                        code="missing-compiled-target",
                        message=f"source {entry['id']} points to a missing compiled target: {target}",
                        path=relpath_to_skill(SOURCE_REGISTRY_PATH),
                    )
                )

    discovery_registry = load_json(DISCOVERY_REGISTRY_PATH).get("watchlists", [])
    for watch in discovery_registry:
        targets = watch.get("promote_into", [])
        if not isinstance(targets, list):
            issues.append(
                Issue(
                    severity="error",
                    code="promote-into-not-list",
                    message=f"watchlist {watch.get('id', '<unknown>')} promote_into must be a list",
                    path=relpath_to_skill(DISCOVERY_REGISTRY_PATH),
                )
            )
            continue
        if not targets:
            issues.append(
                Issue(
                    severity="warning",
                    code="empty-promote-into",
                    message=f"watchlist {watch['id']} has no promote targets",
                    path=relpath_to_skill(DISCOVERY_REGISTRY_PATH),
                )
            )
        for target in targets:
            if not link_target_exists(target):
                issues.append(
                    Issue(
                        severity="error",
                        code="missing-promote-target",
                        message=f"watchlist {watch['id']} points to a missing promote target: {target}",
                        path=relpath_to_skill(DISCOVERY_REGISTRY_PATH),
                    )
                )
    return issues


def check_query_targets() -> list[Issue]:
    issues: list[Issue] = []
    queries = load_json(QUERY_LOG_PATH).get("queries", [])
    for entry in queries:
        query_id = entry.get("id", "<unknown>")
        resolved_by = entry.get("resolved_by", [])
        if entry.get("status") == "resolved" and not resolved_by:
            issues.append(
                Issue(
                    severity="error",
                    code="resolved-query-without-target",
                    message=f"resolved query {query_id} is missing resolved_by targets",
                    path=relpath_to_skill(QUERY_LOG_PATH),
                )
            )
        for target in resolved_by:
            if not link_target_exists(target):
                issues.append(
                    Issue(
                        severity="error",
                        code="missing-query-resolution-target",
                        message=f"query {query_id} points to a missing resolved target: {target}",
                        path=relpath_to_skill(QUERY_LOG_PATH),
                    )
                )
    return issues


def check_issue_inbox_config() -> list[Issue]:
    issues: list[Issue] = []
    payload = load_json(ISSUE_INBOX_CONFIG_PATH)
    required = {
        "enabled": bool,
        "mode": str,
        "repo": str,
        "labels": list,
        "include_issue_comments": bool,
        "close_processed_issues": bool,
        "comment_on_close": bool,
        "max_issues_per_run": int,
        "assigned_repo_allowlist": list,
        "assigned_repo_blocklist": list,
    }
    for key, expected_type in required.items():
        if key not in payload:
            issues.append(
                Issue(
                    severity="error",
                    code="missing-issue-inbox-config-key",
                    message=f"github issue inbox config is missing key: {key}",
                    path=relpath_to_skill(ISSUE_INBOX_CONFIG_PATH),
                )
            )
            continue
        if not isinstance(payload[key], expected_type):
            issues.append(
                Issue(
                    severity="error",
                    code="invalid-issue-inbox-config-type",
                    message=f"github issue inbox config key {key} must be {expected_type.__name__}",
                    path=relpath_to_skill(ISSUE_INBOX_CONFIG_PATH),
                )
            )
    if payload.get("mode") not in {"repo", "assigned"}:
        issues.append(
            Issue(
                severity="error",
                code="invalid-issue-inbox-mode",
                message="github issue inbox mode must be repo or assigned",
                path=relpath_to_skill(ISSUE_INBOX_CONFIG_PATH),
            )
        )
    if isinstance(payload.get("max_issues_per_run"), int) and payload["max_issues_per_run"] <= 0:
        issues.append(
            Issue(
                severity="error",
                code="invalid-issue-inbox-limit",
                message="github issue inbox max_issues_per_run must be > 0",
                path=relpath_to_skill(ISSUE_INBOX_CONFIG_PATH),
            )
        )
    return issues


def check_nightly_review_config() -> list[Issue]:
    issues: list[Issue] = []
    payload = load_json(NIGHTLY_REVIEW_CONFIG_PATH)
    required = {
        "enabled": bool,
        "keywords": list,
        "hackernews": dict,
        "feeds": list,
        "review": dict,
    }
    for key, expected_type in required.items():
        if key not in payload:
            issues.append(
                Issue(
                    severity="error",
                    code="missing-nightly-review-config-key",
                    message=f"nightly review config is missing key: {key}",
                    path=relpath_to_skill(NIGHTLY_REVIEW_CONFIG_PATH),
                )
            )
            continue
        if not isinstance(payload[key], expected_type):
            issues.append(
                Issue(
                    severity="error",
                    code="invalid-nightly-review-config-type",
                    message=f"nightly review config key {key} must be {expected_type.__name__}",
                    path=relpath_to_skill(NIGHTLY_REVIEW_CONFIG_PATH),
                )
            )
    review = payload.get("review", {})
    if isinstance(review, dict) and review.get("human_gate") != "manual-admit":
        issues.append(
            Issue(
                severity="warning",
                code="unexpected-human-gate-mode",
                message="nightly review human gate should stay manual-admit unless you also automate approval workflow",
                path=relpath_to_skill(NIGHTLY_REVIEW_CONFIG_PATH),
            )
        )
    return issues


def markdown_reference_targets(path: Path) -> set[Path]:
    text = path.read_text(encoding="utf-8")
    resolved: set[Path] = set()
    for raw_target in LINK_RE.findall(text):
        if raw_target.startswith(("http://", "https://", "#")):
            continue
        target = raw_target.split("#", 1)[0]
        if not target:
            continue
        absolute = (path.parent / target).resolve()
        if absolute.exists() and WIKI_DIR in absolute.parents:
            resolved.add(absolute)
    return resolved


def check_orphan_wiki_pages() -> list[Issue]:
    referenced: set[Path] = set()
    anchor_docs = [
        Path("README.md"),
        SKILL_DIR / "SKILL.md",
        KNOWLEDGE_DIR / "README.md",
        KNOWLEDGE_DIR / "index.md",
        WIKI_DIR / "README.md",
        *sorted((KNOWLEDGE_DIR / "schema").glob("*.md")),
    ]
    for path in anchor_docs:
        resolved_path = path if path.is_absolute() else (SKILL_DIR.parent.parent.parent / path).resolve()
        if resolved_path.exists():
            referenced.update(markdown_reference_targets(resolved_path))

    source_registry = load_json(SOURCE_REGISTRY_PATH).get("tracked_sources", [])
    for entry in source_registry:
        for target in entry.get("compiled_into", []):
            resolved = (SKILL_DIR / target).resolve()
            if resolved.exists() and WIKI_DIR in resolved.parents:
                referenced.add(resolved)

    discovery_registry = load_json(DISCOVERY_REGISTRY_PATH).get("watchlists", [])
    for watch in discovery_registry:
        for target in watch.get("promote_into", []):
            resolved = (SKILL_DIR / target).resolve()
            if resolved.exists() and WIKI_DIR in resolved.parents:
                referenced.add(resolved)

    queries = load_json(QUERY_LOG_PATH).get("queries", [])
    for entry in queries:
        for target in entry.get("resolved_by", []) + entry.get("promote_into", []):
            resolved = (SKILL_DIR / target).resolve()
            if resolved.exists() and WIKI_DIR in resolved.parents:
                referenced.add(resolved)

    issues: list[Issue] = []
    for path in sorted(WIKI_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        resolved = path.resolve()
        if resolved not in referenced:
            issues.append(
                Issue(
                    severity="warning",
                    code="orphan-wiki-page",
                    message="wiki page has no inbound references from index, docs, registries, or query log",
                    path=relpath_to_skill(path),
                )
            )
    return issues


def build_payload(issues: list[Issue]) -> dict[str, Any]:
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    return {
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "issues": [
            {
                "severity": issue.severity,
                "code": issue.code,
                "message": issue.message,
                "path": issue.path,
            }
            for issue in issues
        ],
    }


def render_markdown(issues: list[Issue]) -> str:
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    lines = [
        "# Knowledge Lint",
        "",
        "Generated from local knowledge files, registries, and `query-log.json` by `scripts/semantic_lint_knowledge.py`.",
        "",
        "## Summary",
        "",
        f"- errors: {len(errors)}",
        f"- warnings: {len(warnings)}",
        "",
        "## Errors",
        "",
    ]
    if errors:
        for issue in errors:
            lines.append(f"- `{issue.code}` in `{issue.path}`: {issue.message}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Warnings", ""])
    if warnings:
        for issue in warnings:
            lines.append(f"- `{issue.code}` in `{issue.path}`: {issue.message}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def build_index_block(issues: list[Issue]) -> str:
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    lines = [
        AUTO_BLOCK_START,
        f"- [lint.md](lint.md) reports {len(errors)} errors and {len(warnings)} warnings across the knowledge layer.",
    ]
    for issue in (errors + warnings)[:3]:
        lines.append(f"  - `{issue.code}` -> `{issue.path}`")
    lines.append(AUTO_BLOCK_END)
    return "\n".join(lines)


def update_index(issues: list[Issue], check: bool) -> bool:
    current = INDEX_PATH.read_text(encoding="utf-8")
    block = build_index_block(issues)
    if AUTO_BLOCK_START in current and AUTO_BLOCK_END in current:
        before, remainder = current.split(AUTO_BLOCK_START, 1)
        _, after = remainder.split(AUTO_BLOCK_END, 1)
        updated = before.rstrip() + "\n\n" + block + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    return write_text_if_changed(INDEX_PATH, updated, check)


def main() -> int:
    args = parse_args()
    issues = collect_issues()
    payload = build_payload(issues)
    write_json_if_changed(LINT_JSON_PATH, payload, args.check)
    write_text_if_changed(LINT_MD_PATH, render_markdown(issues), args.check)
    update_index(issues, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
