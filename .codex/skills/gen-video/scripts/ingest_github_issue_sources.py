#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib import error, parse, request


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
CONFIG_PATH = KNOWLEDGE_DIR / "github-issue-inbox.json"
ISSUE_INBOX_MD_PATH = KNOWLEDGE_DIR / "issue-inbox.md"
ISSUE_INBOX_JSON_PATH = KNOWLEDGE_DIR / "issue-inbox.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"

AUTO_BLOCK_START = "<!-- AUTO:ISSUE-INBOX:START -->"
AUTO_BLOCK_END = "<!-- AUTO:ISSUE-INBOX:END -->"
API_VERSION = "2022-11-28"
DEFAULT_API_BASE = "https://api.github.com"
DEFAULT_WEB_BASE = "https://github.com"
USER_AGENT = "gen-video-issue-inbox/1.0"
URL_RE = re.compile(r"https?://[^\s<>)\]]+")
REQUIRED_CONFIG_KEYS = [
    "enabled",
    "mode",
    "repo",
    "labels",
    "include_issue_comments",
    "close_processed_issues",
    "comment_on_close",
    "max_issues_per_run",
    "assigned_repo_allowlist",
    "assigned_repo_blocklist",
]


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self.title_parts: list[str] = []
        self.description: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value for key, value in attrs}
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() != "meta":
            return
        name = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
        content = attrs_dict.get("content")
        if not content:
            return
        if name in {"description", "og:description", "twitter:description"} and not self.description:
            self.description = clean_whitespace(content)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    @property
    def title(self) -> str:
        return clean_whitespace("".join(self.title_parts))


@dataclass
class SourcePreview:
    url: str
    final_url: str
    title: str
    description: str
    status: str
    error: str | None


@dataclass
class IssueRecord:
    repository: str
    number: int
    title: str
    html_url: str
    labels: list[str]
    urls: list[str]
    source_previews: list[SourcePreview]
    action: str
    comment_created: bool
    closed: bool
    notes: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest GitHub issue bookmarks into the gen-video knowledge inbox."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate generated issue inbox files without writing updates or mutating issues.",
    )
    return parser.parse_args()


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def load_config() -> dict[str, Any]:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_CONFIG_KEYS if key not in payload]
    if missing:
        raise ValueError(f"github-issue-inbox.json is missing keys: {missing}")
    if payload["mode"] not in {"repo", "assigned"}:
        raise ValueError("github-issue-inbox.json mode must be repo or assigned")
    for key in ("labels", "assigned_repo_allowlist", "assigned_repo_blocklist"):
        if not isinstance(payload[key], list):
            raise ValueError(f"github-issue-inbox.json field {key} must be a list")
    if int(payload["max_issues_per_run"]) <= 0:
        raise ValueError("github-issue-inbox.json max_issues_per_run must be > 0")
    return payload


def github_token() -> str:
    token = os.environ.get("GH_ISSUE_INBOX_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    return token.strip()


def api_base() -> str:
    return (os.environ.get("GITHUB_API_URL") or DEFAULT_API_BASE).rstrip("/")


def web_base() -> str:
    return (os.environ.get("GITHUB_SERVER_URL") or DEFAULT_WEB_BASE).rstrip("/")


def github_request(
    method: str,
    path_or_url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> tuple[Any, dict[str, str]]:
    if not token:
        raise RuntimeError("GitHub token is required for issue inbox ingestion")
    url = path_or_url if path_or_url.startswith("http") else f"{api_base()}{path_or_url}"
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        method=method,
        data=data,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            parsed = json.loads(body) if body else None
            headers = {key.lower(): value for key, value in response.headers.items()}
            return parsed, headers
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        detail = body
        try:
            detail_json = json.loads(body)
            detail = detail_json.get("message", body)
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"GitHub API {method} {url} failed with {exc.code}: {detail}") from exc


def fetch_issue_comments(comments_url: str, token: str) -> list[dict[str, Any]]:
    comments, _ = github_request("GET", comments_url, token)
    if not isinstance(comments, list):
        return []
    return comments


def list_repo_issues(config: dict[str, Any], token: str) -> list[dict[str, Any]]:
    repo = config["repo"] or os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        raise RuntimeError("github-issue-inbox.json repo is empty and GITHUB_REPOSITORY is unavailable")
    labels = ",".join(config["labels"])
    per_page = min(int(config["max_issues_per_run"]), 100)
    issues, _ = github_request(
        "GET",
        f"/repos/{repo}/issues?state=open&per_page={per_page}&labels={parse.quote(labels)}",
        token,
    )
    if not isinstance(issues, list):
        raise RuntimeError("GitHub issues API did not return a list")
    return issues


def list_assigned_issues(config: dict[str, Any], token: str) -> list[dict[str, Any]]:
    per_page = min(int(config["max_issues_per_run"]), 100)
    issues, _ = github_request("GET", f"/issues?filter=assigned&state=open&per_page={per_page}", token)
    if not isinstance(issues, list):
        raise RuntimeError("GitHub assigned issues API did not return a list")
    allowed = {item.lower() for item in config["assigned_repo_allowlist"]}
    blocked = {item.lower() for item in config["assigned_repo_blocklist"]}
    wanted_labels = {item.lower() for item in config["labels"]}

    filtered: list[dict[str, Any]] = []
    for issue in issues:
        repo = repository_name_for_issue(issue).lower()
        if allowed and repo not in allowed:
            continue
        if blocked and repo in blocked:
            continue
        labels = {label.get("name", "").lower() for label in issue.get("labels", [])}
        if wanted_labels and not wanted_labels.intersection(labels):
            continue
        filtered.append(issue)
    return filtered


def repository_name_for_issue(issue: dict[str, Any]) -> str:
    html_url = str(issue.get("html_url", ""))
    parsed = parse.urlparse(html_url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    repository_url = str(issue.get("repository_url", ""))
    if repository_url:
        return repository_url.rstrip("/").split("/repos/", 1)[-1]
    return ""


def extract_urls(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for raw in URL_RE.findall(text or ""):
        normalized = raw.rstrip(".,)")
        normalized, _ = parse.urldefrag(normalized)
        if normalized in seen:
            continue
        seen.add(normalized)
        found.append(normalized)
    return found


def fetch_source_preview(url: str) -> SourcePreview:
    req = request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            content_type = response.headers.get("content-type", "")
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip()
            body = response.read(131072).decode(charset, errors="replace")
            parser = MetadataParser()
            parser.feed(body)
            return SourcePreview(
                url=url,
                final_url=response.geturl(),
                title=parser.title or title_from_url(url),
                description=(parser.description or "")[:220],
                status=str(getattr(response, "status", response.getcode())),
                error=None,
            )
    except Exception as exc:  # noqa: BLE001
        return SourcePreview(
            url=url,
            final_url=url,
            title=title_from_url(url),
            description="",
            status="unreachable",
            error=str(exc),
        )


def title_from_url(url: str) -> str:
    parsed = parse.urlparse(url)
    last = parsed.path.rstrip("/").split("/")[-1]
    title = re.sub(r"[-_]+", " ", last).strip()
    return title or url


def build_issue_comment(issue: IssueRecord) -> str:
    lines = [
        "<!-- gen-video-issue-inbox -->",
        "Issue inbox processed this bookmark batch.",
        "",
        f"- extracted_urls: {len(issue.urls)}",
        f"- repository: `{issue.repository}`",
    ]
    if issue.source_previews:
        lines.append("- source_previews:")
        for preview in issue.source_previews[:5]:
            if preview.error:
                lines.append(f"  - {preview.url} -> fetch failed: {preview.error}")
            else:
                lines.append(f"  - {preview.url} -> {preview.title}")
    else:
        lines.append("- source_previews: none")
    lines.append("")
    lines.append("This issue was closed after ingestion into `knowledge/issue-inbox.md`.")
    return "\n".join(lines)


def process_issue(issue: dict[str, Any], config: dict[str, Any], token: str, check: bool) -> IssueRecord:
    repository = repository_name_for_issue(issue)
    number = int(issue["number"])
    title = str(issue.get("title", "")).strip()
    html_url = str(issue.get("html_url", ""))
    labels = [label.get("name", "") for label in issue.get("labels", []) if label.get("name")]
    notes: list[str] = []

    if "pull_request" in issue:
        return IssueRecord(
            repository=repository,
            number=number,
            title=title,
            html_url=html_url,
            labels=labels,
            urls=[],
            source_previews=[],
            action="skipped-pull-request",
            comment_created=False,
            closed=False,
            notes=["GitHub issues API returned a pull request; skipped."],
        )

    url_candidates = extract_urls(title)
    url_candidates.extend(extract_urls(str(issue.get("body", ""))))
    if config["include_issue_comments"] and issue.get("comments"):
        try:
            comments = fetch_issue_comments(str(issue["comments_url"]), token)
        except Exception as exc:  # noqa: BLE001
            comments = []
            notes.append(f"Failed to read issue comments: {exc}")
        for comment in comments:
            url_candidates.extend(extract_urls(str(comment.get("body", ""))))

    deduped_urls: list[str] = []
    seen: set[str] = set()
    for url in url_candidates:
        if url in seen:
            continue
        seen.add(url)
        deduped_urls.append(url)

    previews = [fetch_source_preview(url) for url in deduped_urls]
    if not deduped_urls:
        notes.append("No URLs found in issue title, body, or comments.")

    comment_created = False
    closed = False
    action = "ingested"
    if not check and deduped_urls and config["comment_on_close"]:
        comment_body = build_issue_comment(
            IssueRecord(
                repository=repository,
                number=number,
                title=title,
                html_url=html_url,
                labels=labels,
                urls=deduped_urls,
                source_previews=previews,
                action="ingested",
                comment_created=False,
                closed=False,
                notes=notes,
            )
        )
        try:
            github_request("POST", f"/repos/{repository}/issues/{number}/comments", token, {"body": comment_body})
            comment_created = True
        except Exception as exc:  # noqa: BLE001
            notes.append(f"Failed to comment on issue: {exc}")

    if not check and deduped_urls and config["close_processed_issues"]:
        try:
            github_request("PATCH", f"/repos/{repository}/issues/{number}", token, {"state": "closed"})
            closed = True
            action = "ingested-and-closed"
        except Exception as exc:  # noqa: BLE001
            notes.append(f"Failed to close issue: {exc}")
    elif not deduped_urls:
        action = "skipped-no-urls"

    return IssueRecord(
        repository=repository,
        number=number,
        title=title,
        html_url=html_url,
        labels=labels,
        urls=deduped_urls,
        source_previews=previews,
        action=action,
        comment_created=comment_created,
        closed=closed,
        notes=notes,
    )


def build_payload(config: dict[str, Any], issues: list[IssueRecord]) -> dict[str, Any]:
    return {
        "summary": {
            "mode": config["mode"],
            "processed_issues": len(issues),
            "issues_with_urls": sum(1 for issue in issues if issue.urls),
            "closed_issues": sum(1 for issue in issues if issue.closed),
            "commented_issues": sum(1 for issue in issues if issue.comment_created),
        },
        "issues": [
            {
                "repository": issue.repository,
                "number": issue.number,
                "title": issue.title,
                "html_url": issue.html_url,
                "labels": issue.labels,
                "urls": issue.urls,
                "source_previews": [
                    {
                        "url": preview.url,
                        "final_url": preview.final_url,
                        "title": preview.title,
                        "description": preview.description,
                        "status": preview.status,
                        "error": preview.error,
                    }
                    for preview in issue.source_previews
                ],
                "action": issue.action,
                "comment_created": issue.comment_created,
                "closed": issue.closed,
                "notes": issue.notes,
            }
            for issue in issues
        ],
    }


def render_markdown(config: dict[str, Any], issues: list[IssueRecord]) -> str:
    lines = [
        "# GitHub Issue Inbox",
        "",
        "Generated from `github-issue-inbox.json` by `scripts/ingest_github_issue_sources.py`.",
        "",
        f"- mode: `{config['mode']}`",
        f"- processed_issues: {len(issues)}",
        f"- issues_with_urls: {sum(1 for issue in issues if issue.urls)}",
        f"- closed_issues: {sum(1 for issue in issues if issue.closed)}",
        "",
        "## Processed Issues",
        "",
    ]
    if not issues:
        lines.append("- No matching issues found in the latest run.")
        lines.append("")
        return "\n".join(lines)

    for issue in issues:
        lines.extend(
            [
                f"### {issue.repository}#{issue.number}: {issue.title}",
                "",
                f"- issue: {issue.html_url}",
                f"- labels: {', '.join(f'`{label}`' for label in issue.labels) or '`n/a`'}",
                f"- action: `{issue.action}`",
                f"- comment_created: {str(issue.comment_created).lower()}",
                f"- closed: {str(issue.closed).lower()}",
            ]
        )
        if issue.notes:
            lines.append(f"- notes: {'; '.join(issue.notes)}")
        lines.append("")
        if issue.source_previews:
            for preview in issue.source_previews:
                title = preview.title or preview.url
                lines.append(f"- source: [{title}]({preview.final_url})")
                lines.append(f"  - original_url: {preview.url}")
                lines.append(f"  - status: `{preview.status}`")
                if preview.description:
                    lines.append(f"  - description: {preview.description}")
                if preview.error:
                    lines.append(f"  - error: {preview.error}")
        else:
            lines.append("- source: none")
        lines.append("")
    return "\n".join(lines)


def build_index_block(issues: list[IssueRecord]) -> str:
    with_urls = [issue for issue in issues if issue.urls]
    lines = [
        AUTO_BLOCK_START,
        f"- [issue-inbox.md](issue-inbox.md) processed {len(issues)} bookmarked issues and captured {sum(len(issue.urls) for issue in issues)} URLs.",
        f"- Issues closed after ingestion: {sum(1 for issue in issues if issue.closed)}",
    ]
    for issue in with_urls[:3]:
        lines.append(f"  - `{issue.repository}#{issue.number}` -> {issue.title}")
    lines.append(AUTO_BLOCK_END)
    return "\n".join(lines)


def update_index(issues: list[IssueRecord], check: bool) -> bool:
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
    config = load_config()
    if not config["enabled"]:
        payload = {"summary": {"mode": config["mode"], "enabled": False, "processed_issues": 0}, "issues": []}
        write_json_if_changed(ISSUE_INBOX_JSON_PATH, payload, args.check)
        write_text_if_changed(
            ISSUE_INBOX_MD_PATH,
            "# GitHub Issue Inbox\n\nIssue inbox ingestion is disabled in `github-issue-inbox.json`.\n",
            args.check,
        )
        update_index([], args.check)
        return 0

    token = github_token()
    if not token and args.check:
        if not ISSUE_INBOX_JSON_PATH.exists():
            raise RuntimeError(f"{ISSUE_INBOX_JSON_PATH} is missing")
        if not ISSUE_INBOX_MD_PATH.exists():
            raise RuntimeError(f"{ISSUE_INBOX_MD_PATH} is missing")
        current_index = INDEX_PATH.read_text(encoding="utf-8")
        if AUTO_BLOCK_START not in current_index or AUTO_BLOCK_END not in current_index:
            raise RuntimeError("knowledge/index.md is missing the issue inbox auto block")
        return 0
    issues_payload = (
        list_repo_issues(config, token)
        if config["mode"] == "repo"
        else list_assigned_issues(config, token)
    )
    issues_payload = issues_payload[: int(config["max_issues_per_run"])]
    records = [process_issue(issue, config, token, args.check) for issue in issues_payload]
    records.sort(key=lambda item: (item.repository, item.number))
    payload = build_payload(config, records)
    write_json_if_changed(ISSUE_INBOX_JSON_PATH, payload, args.check)
    write_text_if_changed(ISSUE_INBOX_MD_PATH, render_markdown(config, records), args.check)
    update_index(records, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
