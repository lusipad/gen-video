#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib import parse, request


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
CONFIG_PATH = KNOWLEDGE_DIR / "nightly-review-registry.json"
SOURCE_REGISTRY_PATH = KNOWLEDGE_DIR / "source-registry.json"
CANDIDATES_JSON_PATH = KNOWLEDGE_DIR / "candidates.json"
ISSUE_INBOX_JSON_PATH = KNOWLEDGE_DIR / "issue-inbox.json"
NIGHTLY_REVIEW_MD_PATH = KNOWLEDGE_DIR / "nightly-review.md"
NIGHTLY_REVIEW_JSON_PATH = KNOWLEDGE_DIR / "nightly-review.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"

AUTO_BLOCK_START = "<!-- AUTO:NIGHTLY-REVIEW:START -->"
AUTO_BLOCK_END = "<!-- AUTO:NIGHTLY-REVIEW:END -->"
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
USER_AGENT = "gen-video-nightly-review/1.0"


class HTMLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if stripped:
            self.parts.append(stripped)


@dataclass
class ReviewItem:
    source_id: str
    source_title: str
    source_kind: str
    owner_type: str
    title: str
    url: str
    published_at: str
    summary: str
    matched_keywords: list[str]
    review_into: list[str]
    known_state: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the nightly knowledge review package from HN and watched feeds."
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


def canonical_url(url: str) -> str:
    normalized, _ = parse.urldefrag(url.strip())
    parsed = parse.urlparse(normalized)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{scheme}://{netloc}{path}{query}"


def fetch_json(url: str) -> Any:
    req = request.Request(url, headers={"User-Agent": USER_AGENT})
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str) -> str:
    req = request.Request(url, headers={"User-Agent": USER_AGENT})
    with request.urlopen(req, timeout=30) as response:
        content_type = response.headers.get("content-type", "")
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip()
        return response.read().decode(charset, errors="replace")


def keyword_present(keyword: str, haystack: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(keyword.lower())}(?![a-z0-9])"
    return re.search(pattern, haystack) is not None


def matched_keywords(text_parts: list[str], keywords: list[str]) -> list[str]:
    haystack = " ".join(text_parts).lower()
    return [keyword for keyword in keywords if keyword_present(keyword, haystack)]


def strip_html(text: str) -> str:
    parser = HTMLStripper()
    parser.feed(unescape(text or ""))
    return " ".join(parser.parts)


def truncate(text: str, limit: int = 240) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def known_url_sets() -> tuple[set[str], set[str], set[str]]:
    tracked = {
        canonical_url(entry["url"])
        for entry in load_json(SOURCE_REGISTRY_PATH).get("tracked_sources", [])
        if entry.get("url")
    }
    candidates = {
        canonical_url(entry["url"])
        for entry in load_json(CANDIDATES_JSON_PATH).get("candidates", [])
        if entry.get("url")
    }
    inbox = {
        canonical_url(preview.get("final_url") or preview.get("url"))
        for issue in load_json(ISSUE_INBOX_JSON_PATH).get("issues", [])
        for preview in issue.get("source_previews", [])
        if preview.get("url")
    } if ISSUE_INBOX_JSON_PATH.exists() else set()
    return tracked, candidates, inbox


def known_state_for(url: str, tracked: set[str], candidates: set[str], inbox: set[str]) -> str:
    normalized = canonical_url(url)
    if normalized in tracked:
        return "tracked"
    if normalized in candidates:
        return "candidate"
    if normalized in inbox:
        return "issue-inbox"
    return "new"


def build_hn_items(config: dict[str, Any], tracked: set[str], candidates: set[str], inbox: set[str], global_keywords: list[str]) -> list[ReviewItem]:
    hn = config.get("hackernews", {})
    if not hn.get("enabled"):
        return []
    mode = hn.get("mode", "newstories")
    story_ids = fetch_json(f"{HN_API_BASE}/{mode}.json")
    items: list[ReviewItem] = []
    for story_id in story_ids[: int(hn.get("scan_limit", 60))]:
        story = fetch_json(f"{HN_API_BASE}/item/{story_id}.json")
        if not isinstance(story, dict) or story.get("type") != "story":
            continue
        title = str(story.get("title", "")).strip()
        url = str(story.get("url") or f"https://news.ycombinator.com/item?id={story_id}")
        text = strip_html(str(story.get("text", "")))
        keywords = matched_keywords([title, url, text], global_keywords)
        if not keywords:
            continue
        items.append(
            ReviewItem(
                source_id="hackernews",
                source_title="Hacker News",
                source_kind="hackernews",
                owner_type="community",
                title=title or url,
                url=url,
                published_at=str(story.get("time", "")),
                summary=truncate(text),
                matched_keywords=keywords,
                review_into=[
                    "knowledge/wiki/concepts/karpathy-gap-analysis.md",
                    "knowledge/source-registry.json",
                ],
                known_state=known_state_for(url, tracked, candidates, inbox),
            )
        )
        if len(items) >= int(hn.get("max_items", 10)):
            break
    return items


def xml_text(node: ET.Element | None, *paths: str) -> str:
    if node is None:
        return ""
    for path in paths:
        found = node.find(path)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def atom_link(entry: ET.Element) -> str:
    for child in entry.findall("{http://www.w3.org/2005/Atom}link"):
        href = child.attrib.get("href")
        if href:
            return href
    link = entry.find("{http://www.w3.org/2005/Atom}link")
    if link is not None and link.text:
        return link.text.strip()
    return ""


def build_feed_items(config: dict[str, Any], tracked: set[str], candidates: set[str], inbox: set[str], global_keywords: list[str]) -> list[ReviewItem]:
    items: list[ReviewItem] = []
    for feed in config.get("feeds", []):
        if not feed.get("enabled"):
            continue
        raw = fetch_text(feed["url"])
        root = ET.fromstring(raw)
        feed_items: list[ReviewItem] = []
        if root.tag.endswith("rss"):
            channel = root.find("channel")
            entries = channel.findall("item") if channel is not None else []
            for entry in entries:
                title = xml_text(entry, "title")
                link = xml_text(entry, "link")
                summary = truncate(strip_html(xml_text(entry, "description")))
                published = xml_text(entry, "pubDate")
                keywords = matched_keywords([title, link, summary], list(global_keywords) + list(feed.get("keywords", [])))
                if not keywords:
                    continue
                feed_items.append(
                    ReviewItem(
                        source_id=feed["id"],
                        source_title=feed["title"],
                        source_kind=feed.get("provider", "rss"),
                        owner_type=feed.get("owner_type", "creator"),
                        title=title or link,
                        url=link,
                        published_at=published,
                        summary=summary,
                        matched_keywords=keywords,
                        review_into=list(feed.get("review_into", [])),
                        known_state=known_state_for(link, tracked, candidates, inbox),
                    )
                )
        else:
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")
            for entry in entries:
                title = xml_text(entry, "{http://www.w3.org/2005/Atom}title")
                link = atom_link(entry)
                summary = truncate(
                    strip_html(
                        xml_text(
                            entry,
                            "{http://www.w3.org/2005/Atom}summary",
                            "{http://www.w3.org/2005/Atom}content",
                        )
                    )
                )
                published = xml_text(
                    entry,
                    "{http://www.w3.org/2005/Atom}published",
                    "{http://www.w3.org/2005/Atom}updated",
                )
                keywords = matched_keywords([title, link, summary], list(global_keywords) + list(feed.get("keywords", [])))
                if not keywords:
                    continue
                feed_items.append(
                    ReviewItem(
                        source_id=feed["id"],
                        source_title=feed["title"],
                        source_kind=feed.get("provider", "rss"),
                        owner_type=feed.get("owner_type", "creator"),
                        title=title or link,
                        url=link,
                        published_at=published,
                        summary=summary,
                        matched_keywords=keywords,
                        review_into=list(feed.get("review_into", [])),
                        known_state=known_state_for(link, tracked, candidates, inbox),
                    )
                )
        items.extend(feed_items[: int(config.get("review", {}).get("max_review_items", 20))])
    return items


def dedupe_items(items: list[ReviewItem], max_items: int) -> list[ReviewItem]:
    seen: set[str] = set()
    deduped: list[ReviewItem] = []
    for item in items:
        key = canonical_url(item.url)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_items:
            break
    return deduped


def build_payload(items: list[ReviewItem], config: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": {
            "total_items": len(items),
            "new_items": sum(1 for item in items if item.known_state == "new"),
            "tracked_items": sum(1 for item in items if item.known_state == "tracked"),
            "candidate_items": sum(1 for item in items if item.known_state == "candidate"),
            "issue_inbox_items": sum(1 for item in items if item.known_state == "issue-inbox"),
            "human_gate": config.get("review", {}).get("human_gate", "manual-admit"),
        },
        "items": [
            {
                "source_id": item.source_id,
                "source_title": item.source_title,
                "source_kind": item.source_kind,
                "owner_type": item.owner_type,
                "title": item.title,
                "url": item.url,
                "published_at": item.published_at,
                "summary": item.summary,
                "matched_keywords": item.matched_keywords,
                "review_into": item.review_into,
                "known_state": item.known_state,
            }
            for item in items
        ],
    }


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
            rel = Path(os.path.relpath(resolved, KNOWLEDGE_DIR)).as_posix()
            rendered.append(f"[`{target}`]({rel})")
        else:
            rendered.append(f"`{target}`")
    return ", ".join(rendered)


def render_markdown(items: list[ReviewItem], config: dict[str, Any]) -> str:
    new_items = [item for item in items if item.known_state == "new"]
    known_items = [item for item in items if item.known_state != "new"]
    lines = [
        "# Nightly Knowledge Review",
        "",
        "Generated from `nightly-review-registry.json` by `scripts/build_nightly_review.py`.",
        "",
        f"- total_items: {len(items)}",
        f"- new_items: {len(new_items)}",
        f"- human_gate: `{config.get('review', {}).get('human_gate', 'manual-admit')}`",
        "",
        "## Review Required",
        "",
    ]
    if new_items:
        for item in new_items:
            lines.extend(
                [
                    f"### {item.title}",
                    "",
                    f"- source: `{item.source_title}` (`{item.source_kind}` / `{item.owner_type}`)",
                    f"- url: {item.url}",
                    f"- known_state: `{item.known_state}`",
                    f"- matched_keywords: {', '.join(f'`{word}`' for word in item.matched_keywords) or '`n/a`'}",
                    f"- review_into: {render_targets(item.review_into)}",
                ]
            )
            if item.summary:
                lines.append(f"- summary: {item.summary}")
            lines.append("")
    else:
        lines.append("- No new nightly review items in the latest run.")
        lines.append("")

    lines.extend(["## Already Seen", ""])
    if known_items:
        for item in known_items:
            lines.append(f"- `{item.known_state}` -> [{item.title}]({item.url}) from `{item.source_title}`")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def build_index_block(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        AUTO_BLOCK_START,
        f"- [nightly-review.md](nightly-review.md) contains {summary['total_items']} nightly intelligence items.",
        f"- New review items: {summary['new_items']}",
        f"- Human gate: `{summary['human_gate']}`",
        AUTO_BLOCK_END,
    ]
    return "\n".join(lines)


def update_index(payload: dict[str, Any], check: bool) -> bool:
    current = INDEX_PATH.read_text(encoding="utf-8")
    block = build_index_block(payload)
    if AUTO_BLOCK_START in current and AUTO_BLOCK_END in current:
        before, remainder = current.split(AUTO_BLOCK_START, 1)
        _, after = remainder.split(AUTO_BLOCK_END, 1)
        updated = before.rstrip() + "\n\n" + block + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    return write_text_if_changed(INDEX_PATH, updated, check)


def main() -> int:
    args = parse_args()
    config = load_json(CONFIG_PATH)
    if not config.get("enabled", True):
        payload = {
            "summary": {
                "total_items": 0,
                "new_items": 0,
                "tracked_items": 0,
                "candidate_items": 0,
                "issue_inbox_items": 0,
                "human_gate": "manual-admit",
            },
            "items": [],
        }
        write_json_if_changed(NIGHTLY_REVIEW_JSON_PATH, payload, args.check)
        write_text_if_changed(
            NIGHTLY_REVIEW_MD_PATH,
            "# Nightly Knowledge Review\n\nNightly review is disabled in `nightly-review-registry.json`.\n",
            args.check,
        )
        update_index(payload, args.check)
        return 0

    tracked, candidates, inbox = known_url_sets()
    global_keywords = list(config.get("keywords", []))
    items = []
    items.extend(build_hn_items(config, tracked, candidates, inbox, global_keywords))
    items.extend(build_feed_items(config, tracked, candidates, inbox, global_keywords))
    items = dedupe_items(items, int(config.get("review", {}).get("max_review_items", 20)))
    items.sort(key=lambda item: (0 if item.known_state == "new" else 1, item.source_title.lower(), item.title.lower()))
    payload = build_payload(items, config)
    write_json_if_changed(NIGHTLY_REVIEW_JSON_PATH, payload, args.check)
    write_text_if_changed(NIGHTLY_REVIEW_MD_PATH, render_markdown(items, config), args.check)
    update_index(payload, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
