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
CONFIG_PATH = KNOWLEDGE_DIR / "video-learning-registry.json"
OUTPUT_MD_PATH = KNOWLEDGE_DIR / "video-learning.md"
OUTPUT_JSON_PATH = KNOWLEDGE_DIR / "video-learning.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"

AUTO_BLOCK_START = "<!-- AUTO:VIDEO-LEARNING:START -->"
AUTO_BLOCK_END = "<!-- AUTO:VIDEO-LEARNING:END -->"
ACTION_MARKERS = [
    "先",
    "然后",
    "最后",
    "建议",
    "不要",
    "最好",
    "需要",
    "必须",
    "可以",
    "注意",
    "关键",
    "重点",
    "方法",
    "步骤",
    "should",
    "must",
    "avoid",
    "use",
    "keep",
    "remember",
    "first",
    "then",
    "finally",
]
CONTENT_MARKERS = [
    "故事",
    "剧情",
    "人物",
    "角色",
    "情绪",
    "共情",
    "反转",
    "高潮",
    "结尾",
    "开场",
    "冲突",
    "arc",
    "story",
    "plot",
    "character",
    "emotion",
    "ending",
    "opening",
    "conflict",
]
CRAFT_MARKERS = [
    "镜头",
    "运镜",
    "分镜",
    "脚本",
    "提示词",
    "回灌",
    "存帧",
    "剪辑",
    "节奏",
    "构图",
    "镜位",
    "workflow",
    "camera",
    "shot",
    "frame",
    "storyboard",
    "script",
    "prompt",
    "edit",
    "cut",
    "pacing",
]
SENTENCE_SPLIT_RE = re.compile(r"[。！？!?；;]+|\n+")
WHITESPACE_RE = re.compile(r"\s+")
SRT_BLOCK_RE = re.compile(r"\n\s*\n")


@dataclass
class TextChunk:
    source: str
    timestamp: str
    text: str


@dataclass
class Candidate:
    source: str
    timestamp: str
    text: str
    score: int
    content_score: int
    craft_score: int
    matched_terms: list[str]
    matched_content_terms: list[str]
    matched_craft_terms: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a transcript-driven digest for creator or reference videos."
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


def normalize_text(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text).strip()


def read_text_flexible(path: Path) -> str:
    encodings = ["utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"]
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    return path.read_text(encoding="utf-8")


def resolve_input_path(path_value: str) -> Path:
    raw = Path(path_value)
    if raw.is_absolute():
        return raw
    return (SKILL_DIR / raw).resolve()


def primary_timestamp(raw_timestamp: str) -> str:
    if "-->" in raw_timestamp:
        return raw_timestamp.split("-->", 1)[0].strip()
    return raw_timestamp.strip()


def parse_srt_like(text: str, source: str) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    for block in SRT_BLOCK_RE.split(text.strip()):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        timestamp_index = 1 if len(lines) >= 2 and lines[0].isdigit() and "-->" in lines[1] else 0
        if timestamp_index >= len(lines) or "-->" not in lines[timestamp_index]:
            continue
        timestamp = primary_timestamp(lines[timestamp_index])
        content_lines = lines[timestamp_index + 1 :]
        content = normalize_text(" ".join(content_lines))
        if content:
            chunks.append(TextChunk(source=source, timestamp=timestamp, text=content))
    return chunks


def parse_vtt(text: str, source: str) -> list[TextChunk]:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = SRT_BLOCK_RE.split(cleaned.strip())
    chunks: list[TextChunk] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines or lines[0].upper() == "WEBVTT" or lines[0].startswith("NOTE"):
            continue
        timestamp_line = next((line for line in lines if "-->" in line), "")
        if not timestamp_line:
            continue
        timestamp = primary_timestamp(timestamp_line)
        content_started = False
        content_lines: list[str] = []
        for line in lines:
            if line == timestamp_line:
                content_started = True
                continue
            if content_started:
                content_lines.append(line)
        content = normalize_text(" ".join(content_lines))
        if content:
            chunks.append(TextChunk(source=source, timestamp=timestamp, text=content))
    return chunks


def parse_plain_text(text: str, source: str) -> list[TextChunk]:
    blocks = [normalize_text(block) for block in re.split(r"\n\s*\n", text) if normalize_text(block)]
    return [TextChunk(source=source, timestamp="", text=block) for block in blocks]


def parse_text_chunks(path: Path, source: str) -> list[TextChunk]:
    text = read_text_flexible(path)
    suffix = path.suffix.lower()
    if suffix == ".srt":
        return parse_srt_like(text, source)
    if suffix == ".vtt":
        return parse_vtt(text, source)
    return parse_plain_text(text, source)


def alias_present(alias: str, haystack: str) -> bool:
    lowered = alias.lower()
    if re.search(r"[a-z0-9]", lowered):
        pattern = rf"(?<![a-z0-9]){re.escape(lowered)}(?![a-z0-9])"
        return re.search(pattern, haystack) is not None
    return lowered in haystack


def build_term_vocab(config: dict[str, Any], tags: list[str], focus: list[str]) -> list[dict[str, Any]]:
    vocab = list(config.get("term_vocab", []))
    for tag in tags:
        vocab.append({"id": tag, "aliases": [tag], "category": "generic"})
    for item in focus:
        vocab.append({"id": item, "aliases": [item], "category": "generic"})
    return vocab


def matched_terms(text: str, vocab: list[dict[str, Any]]) -> list[str]:
    haystack = text.lower()
    hits: list[str] = []
    for entry in vocab:
        aliases = entry.get("aliases", [])
        if any(alias_present(alias, haystack) for alias in aliases):
            hits.append(str(entry.get("id", "")).strip())
    return [hit for hit in hits if hit]


def term_categories_by_id(vocab: list[dict[str, Any]]) -> dict[str, str]:
    categories: dict[str, str] = {}
    for entry in vocab:
        term_id = str(entry.get("id", "")).strip()
        if not term_id:
            continue
        categories[term_id] = str(entry.get("category", "generic")).strip() or "generic"
    return categories


def split_terms_by_category(hits: list[str], categories: dict[str, str]) -> tuple[list[str], list[str]]:
    content_hits: list[str] = []
    craft_hits: list[str] = []
    for hit in hits:
        category = categories.get(hit, "generic")
        if category == "content":
            content_hits.append(hit)
        elif category == "craft":
            craft_hits.append(hit)
    return content_hits, craft_hits


def base_candidate_score(text: str, source: str, hits: list[str]) -> int:
    lowered = text.lower()
    length = len(text)
    score = 0
    if 16 <= length <= 220:
        score += 2
    elif length < 8:
        score -= 3
    elif length < 16:
        score -= 1
    elif length > 320:
        score -= 1
    marker_hits = sum(1 for marker in ACTION_MARKERS if alias_present(marker, lowered))
    score += min(4, marker_hits)
    score += min(4, len(hits))
    if re.search(r"\d", text):
        score += 1
    if source == "notes":
        score += 2
    if text.startswith(("-", "*")) or re.match(r"^\d+[.)、]", text):
        score += 1
    return score


def mode_bonus(text: str, markers: list[str]) -> int:
    lowered = text.lower()
    hits = sum(1 for marker in markers if alias_present(marker, lowered))
    return min(5, hits)


def chunk_sentences(chunk: TextChunk) -> list[str]:
    pieces = [normalize_text(piece) for piece in SENTENCE_SPLIT_RE.split(chunk.text)]
    usable = [piece for piece in pieces if len(piece) >= 8]
    return usable or [chunk.text]


def build_candidates(chunks: list[TextChunk], config: dict[str, Any], tags: list[str], focus: list[str]) -> list[Candidate]:
    vocab = build_term_vocab(config, tags, focus)
    categories = term_categories_by_id(vocab)
    candidates: list[Candidate] = []
    seen: set[str] = set()
    for chunk in chunks:
        for sentence in chunk_sentences(chunk):
            normalized = normalize_text(sentence)
            dedupe_key = normalized.lower()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            hits = matched_terms(normalized, vocab)
            content_hits, craft_hits = split_terms_by_category(hits, categories)
            base_score = base_candidate_score(normalized, chunk.source, hits)
            content_score = base_score + mode_bonus(normalized, CONTENT_MARKERS) + min(4, len(content_hits))
            craft_score = base_score + mode_bonus(normalized, CRAFT_MARKERS) + min(4, len(craft_hits))
            score = max(content_score, craft_score)
            candidates.append(
                Candidate(
                    source=chunk.source,
                    timestamp=chunk.timestamp,
                    text=normalized,
                    score=score,
                    content_score=content_score,
                    craft_score=craft_score,
                    matched_terms=hits,
                    matched_content_terms=content_hits,
                    matched_craft_terms=craft_hits,
                )
            )
    candidates.sort(
        key=lambda item: (
            -item.score,
            0 if item.source == "notes" else 1,
            len(item.text),
        )
    )
    return candidates


def top_terms(chunks: list[TextChunk], config: dict[str, Any], tags: list[str], focus: list[str], limit: int, category_filter: str | None = None) -> list[str]:
    vocab = build_term_vocab(config, tags, focus)
    categories = term_categories_by_id(vocab)
    counts: dict[str, int] = {}
    for chunk in chunks:
        for hit in matched_terms(chunk.text, vocab):
            if category_filter and categories.get(hit) != category_filter:
                continue
            counts[hit] = counts.get(hit, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [term for term, _ in ranked[:limit]]


def build_entry_digest(entry: dict[str, Any], config: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    transcript_path_value = str(entry.get("transcript_path", "")).strip()
    notes_path_value = str(entry.get("notes_path", "")).strip()
    if not transcript_path_value and not notes_path_value:
        errors.append("enabled entry must provide transcript_path or notes_path")
        return None, errors

    chunks: list[TextChunk] = []
    source_files: list[str] = []
    for source_name, raw_path in (("transcript", transcript_path_value), ("notes", notes_path_value)):
        if not raw_path:
            continue
        resolved = resolve_input_path(raw_path)
        if not resolved.exists():
            errors.append(f"{source_name}_path does not exist: {raw_path}")
            continue
        source_files.append(raw_path)
        try:
            chunks.extend(parse_text_chunks(resolved, source_name))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to parse {source_name}_path `{raw_path}`: {exc}")

    if not chunks:
        return None, errors

    extract = dict(config.get("default_extract", {}))
    extract.update(entry.get("extract", {}))
    learning_mode = str(entry.get("learning_mode", "craft")).strip() or "craft"
    focus = [str(item) for item in entry.get("focus", [])]
    max_highlights = int(extract.get("max_highlights", 8))
    max_takeaways = int(extract.get("max_takeaways", 5))
    max_content_takeaways = int(extract.get("max_content_takeaways", max_takeaways))
    max_craft_takeaways = int(extract.get("max_craft_takeaways", max_takeaways))
    max_terms = int(extract.get("max_terms", 10))
    tags = [str(tag) for tag in entry.get("tags", [])]

    candidates = build_candidates(chunks, config, tags, focus)
    highlights = candidates[:max_highlights]
    takeaway_candidates = [
        candidate
        for candidate in candidates
        if any(alias_present(marker, candidate.text.lower()) for marker in ACTION_MARKERS)
        or candidate.source == "notes"
    ]
    if len(takeaway_candidates) < max_takeaways:
        takeaway_candidates = candidates
    content_takeaways = sorted(
        takeaway_candidates,
        key=lambda item: (-item.content_score, 0 if item.source == "notes" else 1, len(item.text)),
    )[:max_content_takeaways]
    craft_takeaways = sorted(
        takeaway_candidates,
        key=lambda item: (-item.craft_score, 0 if item.source == "notes" else 1, len(item.text)),
    )[:max_craft_takeaways]
    if learning_mode == "content":
        takeaways = content_takeaways[:max_takeaways]
    else:
        takeaways = craft_takeaways[:max_takeaways]
    terms = top_terms(chunks, config, tags, focus, max_terms)
    content_terms = top_terms(chunks, config, tags, focus, max_terms, "content")
    craft_terms = top_terms(chunks, config, tags, focus, max_terms, "craft")

    digest = {
        "id": entry["id"],
        "title": entry["title"],
        "platform": entry["platform"],
        "creator": entry["creator"],
        "url": entry["url"],
        "published_at": entry.get("published_at", ""),
        "language": entry.get("language", ""),
        "learning_mode": learning_mode,
        "focus": focus,
        "status": entry.get("status", "pending"),
        "source_files": source_files,
        "segment_count": len(chunks),
        "char_count": sum(len(chunk.text) for chunk in chunks),
        "matched_terms": terms,
        "matched_content_terms": content_terms,
        "matched_craft_terms": craft_terms,
        "review_into": list(entry.get("review_into", [])),
        "highlights": [
            {
                "source": item.source,
                "timestamp": item.timestamp,
                "text": item.text,
                "score": item.score,
                "matched_terms": item.matched_terms,
                "matched_content_terms": item.matched_content_terms,
                "matched_craft_terms": item.matched_craft_terms,
            }
            for item in highlights
        ],
        "takeaways": [
            {
                "source": item.source,
                "timestamp": item.timestamp,
                "text": item.text,
            }
            for item in takeaways
        ],
        "content_takeaways": [
            {
                "source": item.source,
                "timestamp": item.timestamp,
                "text": item.text,
            }
            for item in content_takeaways
        ],
        "craft_takeaways": [
            {
                "source": item.source,
                "timestamp": item.timestamp,
                "text": item.text,
            }
            for item in craft_takeaways
        ],
    }
    return digest, errors


def build_payload(config: dict[str, Any]) -> dict[str, Any]:
    entries = config.get("entries", [])
    digests: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for entry in entries:
        if not entry.get("enabled"):
            continue
        digest, entry_errors = build_entry_digest(entry, config)
        if digest is not None:
            digests.append(digest)
        for error in entry_errors:
            errors.append({"id": entry.get("id", "<unknown>"), "message": error})

    digests.sort(key=lambda item: (0 if item.get("status") == "pending" else 1, item["title"].lower()))
    return {
        "summary": {
            "total_entries": len(digests),
            "pending_entries": sum(1 for item in digests if item.get("status") == "pending"),
            "reviewed_entries": sum(1 for item in digests if item.get("status") == "reviewed"),
            "compiled_entries": sum(1 for item in digests if item.get("status") == "compiled"),
            "content_entries": sum(1 for item in digests if item.get("learning_mode") == "content"),
            "craft_entries": sum(1 for item in digests if item.get("learning_mode") == "craft"),
            "errors": len(errors),
        },
        "entries": digests,
        "errors": errors,
    }


def render_markdown(payload: dict[str, Any], config_enabled: bool) -> str:
    if not config_enabled:
        return "# Video Learning Digest\n\nVideo learning is disabled in `video-learning-registry.json`.\n"

    summary = payload["summary"]
    entries = payload["entries"]
    errors = payload["errors"]
    lines = [
        "# Video Learning Digest",
        "",
        "Generated from `video-learning-registry.json` by `scripts/build_video_learning_digest.py`.",
        "",
        f"- total_entries: {summary['total_entries']}",
        f"- pending_entries: {summary['pending_entries']}",
        f"- reviewed_entries: {summary['reviewed_entries']}",
        f"- compiled_entries: {summary['compiled_entries']}",
        f"- content_entries: {summary['content_entries']}",
        f"- craft_entries: {summary['craft_entries']}",
        f"- errors: {summary['errors']}",
        "",
        "## Ready For Distillation",
        "",
    ]
    if entries:
        for entry in entries:
            lines.extend(
                [
                    f"### {entry['title']}",
                    "",
                    f"- learning_mode: `{entry['learning_mode']}`",
                    f"- platform: `{entry['platform']}`",
                    f"- creator: `{entry['creator']}`",
                    f"- status: `{entry['status']}`",
                    f"- url: {entry['url']}",
                    f"- source_files: {render_targets(entry['source_files'])}",
                    f"- segment_count: {entry['segment_count']}",
                    f"- char_count: {entry['char_count']}",
                    f"- focus: {', '.join(f'`{item}`' for item in entry['focus']) or '`n/a`'}",
                    f"- matched_terms: {', '.join(f'`{term}`' for term in entry['matched_terms']) or '`n/a`'}",
                    f"- matched_content_terms: {', '.join(f'`{term}`' for term in entry['matched_content_terms']) or '`n/a`'}",
                    f"- matched_craft_terms: {', '.join(f'`{term}`' for term in entry['matched_craft_terms']) or '`n/a`'}",
                    f"- review_into: {render_targets(entry['review_into'])}",
                    "",
                    "#### Highlights",
                    "",
                ]
            )
            if entry["highlights"]:
                for highlight in entry["highlights"]:
                    prefix = f"`{highlight['timestamp']}` " if highlight.get("timestamp") else ""
                    lines.append(f"- {prefix}{highlight['text']}")
            else:
                lines.append("- None.")
            lines.extend(["", "#### Priority Takeaways", ""])
            if entry["takeaways"]:
                for takeaway in entry["takeaways"]:
                    prefix = f"`{takeaway['timestamp']}` " if takeaway.get("timestamp") else ""
                    lines.append(f"- {prefix}{takeaway['text']}")
            else:
                lines.append("- None.")
            lines.extend(["", "#### Content Takeaways", ""])
            if entry["content_takeaways"]:
                for takeaway in entry["content_takeaways"]:
                    prefix = f"`{takeaway['timestamp']}` " if takeaway.get("timestamp") else ""
                    lines.append(f"- {prefix}{takeaway['text']}")
            else:
                lines.append("- None.")
            lines.extend(["", "#### Craft Takeaways", ""])
            if entry["craft_takeaways"]:
                for takeaway in entry["craft_takeaways"]:
                    prefix = f"`{takeaway['timestamp']}` " if takeaway.get("timestamp") else ""
                    lines.append(f"- {prefix}{takeaway['text']}")
            else:
                lines.append("- None.")
            lines.append("")
    else:
        lines.append("- No enabled video learning entries in the latest run.")
        lines.append("")

    lines.extend(["## Errors", ""])
    if errors:
        for error in errors:
            lines.append(f"- `{error['id']}`: {error['message']}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def build_index_block(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        AUTO_BLOCK_START,
        f"- [video-learning.md](video-learning.md) contains {summary['total_entries']} transcript-driven video learning items.",
        f"- Pending distillation items: {summary['pending_entries']}",
        f"- Modes: content={summary['content_entries']}, craft={summary['craft_entries']}",
        f"- Digest errors: {summary['errors']}",
    ]
    for entry in payload.get("entries", [])[:2]:
        lines.append(f"  - `{entry['learning_mode']}` / `{entry['status']}` -> {entry['title']}")
    lines.append(AUTO_BLOCK_END)
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
    enabled = bool(config.get("enabled", True))
    if enabled:
        payload = build_payload(config)
    else:
        payload = {
            "summary": {
                "total_entries": 0,
                "pending_entries": 0,
                "reviewed_entries": 0,
                "compiled_entries": 0,
                "content_entries": 0,
                "craft_entries": 0,
                "errors": 0,
            },
            "entries": [],
            "errors": [],
        }
    write_json_if_changed(OUTPUT_JSON_PATH, payload, args.check)
    write_text_if_changed(OUTPUT_MD_PATH, render_markdown(payload, enabled), args.check)
    update_index(payload, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
