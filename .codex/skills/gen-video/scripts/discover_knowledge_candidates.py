#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib import parse, request


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
SOURCE_REGISTRY_PATH = KNOWLEDGE_DIR / "source-registry.json"
DISCOVERY_REGISTRY_PATH = KNOWLEDGE_DIR / "discovery-registry.json"
CANDIDATES_JSON_PATH = KNOWLEDGE_DIR / "candidates.json"
CANDIDATES_MD_PATH = KNOWLEDGE_DIR / "candidates.md"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"
AUTO_BLOCK_START = "<!-- AUTO:CANDIDATES:START -->"
AUTO_BLOCK_END = "<!-- AUTO:CANDIDATES:END -->"
USER_AGENT = "gen-video-discovery/1.0"
HTTP_TIMEOUT_SECONDS = 30
REQUIRED_WATCH_KEYS = [
    "id",
    "title",
    "owner_type",
    "url",
    "mode",
    "allowed_domains",
    "include_url_patterns",
    "exclude_url_patterns",
    "keywords",
    "max_candidates",
    "promote_into",
]


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href:
            self._current_href = href
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            stripped = data.strip()
            if stripped:
                self._current_text.append(stripped)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current_href is None:
            return
        text = " ".join(self._current_text).strip()
        self.links.append((self._current_href, text))
        self._current_href = None
        self._current_text = []


@dataclass
class Candidate:
    watch_id: str
    watch_title: str
    owner_type: str
    title: str
    url: str
    matched_keywords: list[str]
    promote_into: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover new knowledge candidates from official and blogger watchlists."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate generated candidate files without writing updates.",
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


def load_tracked_urls() -> set[str]:
    payload = json.loads(SOURCE_REGISTRY_PATH.read_text(encoding="utf-8"))
    tracked = payload.get("tracked_sources", [])
    urls: set[str] = set()
    for item in tracked:
        url = item.get("url")
        if isinstance(url, str):
            urls.add(canonical_url(url))
    return urls


def load_watchlists() -> list[dict[str, Any]]:
    payload = json.loads(DISCOVERY_REGISTRY_PATH.read_text(encoding="utf-8"))
    watchlists = payload.get("watchlists")
    if not isinstance(watchlists, list):
        raise ValueError("discovery-registry.json must contain a watchlists array")
    for watch in watchlists:
        missing = [key for key in REQUIRED_WATCH_KEYS if key not in watch]
        if missing:
            raise ValueError(f"watchlist {watch.get('id', '<unknown>')} is missing keys: {missing}")
        if watch["mode"] != "html-links":
            raise ValueError(f"watchlist {watch['id']} mode must be html-links")
    return watchlists


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


def fetch_html(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    req = request.Request(url, headers=headers)
    with request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as response:
        content_type = response.headers.get("content-type", "")
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip()
        return response.read().decode(charset, errors="replace")


def extract_links(base_url: str, html: str) -> list[tuple[str, str]]:
    parser = AnchorParser()
    parser.feed(html)
    seen: set[str] = set()
    results: list[tuple[str, str]] = []
    for href, text in parser.links:
        absolute = parse.urljoin(base_url, href)
        parsed = parse.urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        normalized = canonical_url(absolute)
        if normalized in seen:
            continue
        seen.add(normalized)
        results.append((normalized, text))
    return results


def pattern_match(patterns: list[str], value: str) -> bool:
    return any(pattern.lower() in value.lower() for pattern in patterns)


def keyword_present(keyword: str, haystack: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(keyword.lower())}(?![a-z0-9])"
    return re.search(pattern, haystack) is not None


def link_matches_watchlist(url: str, text: str, watch: dict[str, Any]) -> tuple[bool, list[str]]:
    parsed = parse.urlparse(url)
    if parsed.netloc.lower() not in {domain.lower() for domain in watch["allowed_domains"]}:
        return False, []
    if watch["include_url_patterns"] and not pattern_match(watch["include_url_patterns"], url):
        return False, []
    if watch["exclude_url_patterns"] and pattern_match(watch["exclude_url_patterns"], url):
        return False, []
    title = clean_title(text, url)
    haystack = f"{url} {title}".lower()
    matched_keywords = [keyword for keyword in watch["keywords"] if keyword_present(keyword, haystack)]
    if watch["keywords"] and not matched_keywords:
        return False, []
    return True, matched_keywords


def title_from_url(url: str) -> str:
    parsed = parse.urlparse(url)
    last = parsed.path.rstrip("/").split("/")[-1]
    words = re.sub(r"[-_]+", " ", last).strip()
    return words or url


def clean_title(text: str, url: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        normalized = title_from_url(url)
    if len(normalized) > 140:
        normalized = normalized[:137].rstrip() + "..."
    return normalized


def discover_candidates() -> list[Candidate]:
    tracked_urls = load_tracked_urls()
    watchlists = load_watchlists()
    candidates: list[Candidate] = []
    seen_urls: set[str] = set()

    for watch in watchlists:
        try:
            html = fetch_html(watch["url"])
        except Exception as exc:  # noqa: BLE001
            candidates.append(
                Candidate(
                    watch_id=watch["id"],
                    watch_title=watch["title"],
                    owner_type=watch["owner_type"],
                    title=f"watchlist fetch failed: {exc}",
                    url=watch["url"],
                    matched_keywords=[],
                    promote_into=watch["promote_into"],
                )
            )
            continue

        count = 0
        for url, text in extract_links(watch["url"], html):
            if canonical_url(url) in tracked_urls or url in seen_urls:
                continue
            matched, keywords = link_matches_watchlist(url, text, watch)
            if not matched:
                continue
            seen_urls.add(url)
            title = clean_title(text, url)
            candidates.append(
                Candidate(
                    watch_id=watch["id"],
                    watch_title=watch["title"],
                    owner_type=watch["owner_type"],
                    title=title,
                    url=url,
                    matched_keywords=keywords,
                    promote_into=watch["promote_into"],
                )
            )
            count += 1
            if count >= int(watch["max_candidates"]):
                break
    return candidates


def build_payload(candidates: list[Candidate]) -> dict[str, Any]:
    official = sum(1 for item in candidates if item.owner_type == "official")
    blogger = sum(1 for item in candidates if item.owner_type == "blogger")
    failures = sum(1 for item in candidates if item.title.startswith("watchlist fetch failed:"))
    return {
        "summary": {
            "total_candidates": len(candidates),
            "official_candidates": official,
            "blogger_candidates": blogger,
            "fetch_failures": failures,
        },
        "candidates": [
            {
                "watch_id": item.watch_id,
                "watch_title": item.watch_title,
                "owner_type": item.owner_type,
                "title": item.title,
                "url": item.url,
                "matched_keywords": item.matched_keywords,
                "promote_into": item.promote_into,
            }
            for item in candidates
        ],
    }


def render_markdown(candidates: list[Candidate]) -> str:
    lines = [
        "# Knowledge Candidates",
        "",
        "Generated from `discovery-registry.json` by `scripts/discover_knowledge_candidates.py`.",
        "",
    ]
    real_candidates = [item for item in candidates if not item.title.startswith("watchlist fetch failed:")]
    if real_candidates:
        lines.extend(["## Promotion Queue", ""])
        for item in real_candidates:
            keywords = ", ".join(f"`{word}`" for word in item.matched_keywords) or "`n/a`"
            promote = ", ".join(f"`{target}`" for target in item.promote_into) or "`n/a`"
            lines.extend(
                [
                    f"### {item.title}",
                    "",
                    f"- watchlist: `{item.watch_id}`",
                    f"- owner_type: `{item.owner_type}`",
                    f"- url: {item.url}",
                    f"- matched_keywords: {keywords}",
                    f"- promote_into: {promote}",
                    "",
                ]
            )
    else:
        lines.extend(["## Promotion Queue", "", "- No unseen candidates discovered in the latest run.", ""])

    failures = [item for item in candidates if item.title.startswith("watchlist fetch failed:")]
    lines.extend(["## Watchlist Health", ""])
    if failures:
        for item in failures:
            lines.append(f"- `{item.watch_id}` -> {item.title}")
    else:
        lines.append("- All discovery watchlists fetched successfully.")
    lines.append("")
    return "\n".join(lines)


def build_index_block(candidates: list[Candidate]) -> str:
    real_candidates = [item for item in candidates if not item.title.startswith("watchlist fetch failed:")]
    lines = [
        AUTO_BLOCK_START,
        f"- [candidates.md](candidates.md) contains {len(real_candidates)} unseen candidate links from discovery watchlists.",
    ]
    for item in real_candidates[:5]:
        lines.append(f"  - `{item.watch_id}` -> [{item.title}]({item.url})")
    failures = [item for item in candidates if item.title.startswith("watchlist fetch failed:")]
    lines.append(f"- Discovery watchlist fetch failures: {len(failures)}")
    for item in failures[:5]:
        lines.append(f"  - `{item.watch_id}`")
    lines.append(AUTO_BLOCK_END)
    return "\n".join(lines)


def update_index(candidates: list[Candidate], check: bool) -> bool:
    current = INDEX_PATH.read_text(encoding="utf-8")
    block = build_index_block(candidates)
    if AUTO_BLOCK_START in current and AUTO_BLOCK_END in current:
        before, remainder = current.split(AUTO_BLOCK_START, 1)
        _, after = remainder.split(AUTO_BLOCK_END, 1)
        updated = before.rstrip() + "\n\n" + block + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    return write_text_if_changed(INDEX_PATH, updated, check)


def main() -> int:
    args = parse_args()
    candidates = discover_candidates()
    candidates.sort(key=lambda item: (item.owner_type, item.watch_id, item.title.lower()))
    payload = build_payload(candidates)
    write_json_if_changed(CANDIDATES_JSON_PATH, payload, args.check)
    write_text_if_changed(CANDIDATES_MD_PATH, render_markdown(candidates), args.check)
    update_index(candidates, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
