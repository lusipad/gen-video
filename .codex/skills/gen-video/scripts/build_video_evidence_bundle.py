#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
BENCHMARKS_DIR = SKILL_DIR / "benchmarks"
CONFIG_PATH = BENCHMARKS_DIR / "video-evidence-registry.json"
OUTPUT_MD_PATH = BENCHMARKS_DIR / "video-evidence.md"
OUTPUT_JSON_PATH = BENCHMARKS_DIR / "video-evidence.json"

WHITESPACE_RE = re.compile(r"\s+")
SRT_BLOCK_RE = re.compile(r"\n\s*\n")
TIMESTAMP_RANGE_RE = re.compile(r"(?P<start>\d{2}:\d{2}(?::\d{2})?)(?:\s*[-~—>]+\s*(?P<end>\d{2}:\d{2}(?::\d{2})?))?")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a normalized evidence bundle for generated video review."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate generated files without writing updates.",
    )
    parser.add_argument(
        "--entry",
        action="append",
        default=[],
        help="Only build specific registry entry ids. Can be provided multiple times.",
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


def resolve_path(path_value: str) -> Path:
    raw = Path(path_value)
    if raw.is_absolute():
        return raw
    return (SKILL_DIR / raw).resolve()


def relpath_from_benchmarks(target: str) -> str:
    return Path(os.path.relpath(SKILL_DIR / target, BENCHMARKS_DIR)).as_posix()


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
            rendered.append(f"[`{target}`]({relpath_from_benchmarks(target)})")
        else:
            rendered.append(f"`{target}`")
    return ", ".join(rendered)


def find_tool(name: str) -> str | None:
    return shutil.which(name)


def probe_video(path: Path) -> tuple[dict[str, Any], str | None]:
    ffprobe = find_tool("ffprobe")
    if not ffprobe:
        return {}, "ffprobe not available"
    if not path.exists():
        return {}, f"missing video file: {path}"
    command = [
        ffprobe,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return {}, completed.stderr.strip() or "ffprobe failed"
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {}, "ffprobe returned invalid JSON"

    video_stream = next(
        (stream for stream in payload.get("streams", []) if stream.get("codec_type") == "video"),
        {},
    )
    format_info = payload.get("format", {})
    result: dict[str, Any] = {
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "codec_name": video_stream.get("codec_name"),
    }
    duration_raw = format_info.get("duration") or video_stream.get("duration")
    if duration_raw not in (None, ""):
        try:
            result["duration_seconds"] = round(float(duration_raw), 3)
        except (TypeError, ValueError):
            pass
    return result, None


def primary_timestamp(raw_timestamp: str) -> str:
    if "-->" in raw_timestamp:
        return raw_timestamp.split("-->", 1)[0].strip()
    return raw_timestamp.strip()


def parse_srt_like(text: str) -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
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
            chunks.append({"timestamp": timestamp, "text": content})
    return chunks


def parse_vtt(text: str) -> list[dict[str, str]]:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = SRT_BLOCK_RE.split(cleaned.strip())
    chunks: list[dict[str, str]] = []
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
            chunks.append({"timestamp": timestamp, "text": content})
    return chunks


def parse_plain_text(text: str) -> list[dict[str, str]]:
    blocks = [normalize_text(block) for block in re.split(r"\n\s*\n", text) if normalize_text(block)]
    return [{"timestamp": "", "text": block} for block in blocks]


def parse_transcript(path: Path) -> list[dict[str, str]]:
    text = read_text_flexible(path)
    suffix = path.suffix.lower()
    if suffix == ".srt":
        return parse_srt_like(text)
    if suffix == ".vtt":
        return parse_vtt(text)
    return parse_plain_text(text)


def parse_markdown_sections(path: Path) -> list[dict[str, Any]]:
    text = read_text_flexible(path).replace("\r\n", "\n").replace("\r", "\n")
    sections: list[dict[str, Any]] = []
    current_heading = "intro"
    current_lines: list[str] = []
    for line in text.split("\n"):
        if line.startswith("#"):
            if current_lines:
                content = normalize_text(" ".join(current_lines))
                if content:
                    sections.append(section_from_heading(current_heading, content))
            current_heading = line.lstrip("#").strip() or "section"
            current_lines = []
            continue
        stripped = line.strip()
        if stripped:
            current_lines.append(stripped.lstrip("-").strip())
    if current_lines:
        content = normalize_text(" ".join(current_lines))
        if content:
            sections.append(section_from_heading(current_heading, content))
    return sections


def section_from_heading(heading: str, content: str) -> dict[str, Any]:
    match = TIMESTAMP_RANGE_RE.search(heading)
    return {
        "heading": heading,
        "start": match.group("start") if match else "",
        "end": match.group("end") if match else "",
        "content": content,
    }


def time_to_seconds(timestamp: str) -> float | None:
    if not timestamp:
        return None
    parts = timestamp.split(":")
    try:
        values = [float(part) for part in parts]
    except ValueError:
        return None
    if len(values) == 2:
        minutes, seconds = values
        return minutes * 60 + seconds
    if len(values) == 3:
        hours, minutes, seconds = values
        return hours * 3600 + minutes * 60 + seconds
    return None


def seconds_to_timestamp(value: float) -> str:
    total_seconds = max(value, 0)
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds - hours * 3600 - minutes * 60
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    return f"{minutes:02d}:{seconds:06.3f}"


def extract_frames(entry: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    video_path_value = str(entry.get("video_path", "")).strip()
    if not video_path_value:
        return {"status": "skipped", "reason": "no video_path configured", "frames": []}
    resolved_video = resolve_path(video_path_value)
    if not resolved_video.exists():
        return {"status": "skipped", "reason": f"missing video file: {video_path_value}", "frames": []}
    ffmpeg = find_tool("ffmpeg")
    if not ffmpeg:
        return {"status": "skipped", "reason": "ffmpeg not available", "frames": []}

    extract = entry.get("extract", {}) or {}
    explicit_timestamps = [str(item).strip() for item in extract.get("sample_timestamps", []) if str(item).strip()]
    if not explicit_timestamps:
        sample_every = extract.get("sample_every_seconds")
        max_frames = int(extract.get("max_sample_frames", 4))
        duration = metadata.get("duration_seconds")
        if sample_every and duration:
            seconds = float(sample_every)
            explicit_timestamps = [
                seconds_to_timestamp(index * seconds)
                for index in range(max_frames)
                if index * seconds <= float(duration)
            ]
    if not explicit_timestamps:
        return {"status": "skipped", "reason": "no sampling timestamps configured", "frames": []}

    output_dir_value = str(extract.get("frame_output_dir", f"benchmarks/raw/video-review/extracted/{entry.get('id', 'entry')}")).strip()
    output_dir = resolve_path(output_dir_value)
    output_dir.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, Any]] = []
    for timestamp in explicit_timestamps:
        safe_name = timestamp.replace(":", "").replace(".", "")
        output_path = output_dir / f"{entry.get('id', 'entry')}_{safe_name}.jpg"
        command = [
            ffmpeg,
            "-y",
            "-ss",
            timestamp,
            "-i",
            str(resolved_video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        frame_result = {
            "timestamp": timestamp,
            "path": Path(os.path.relpath(output_path, SKILL_DIR)).as_posix(),
        }
        if completed.returncode != 0:
            frame_result["status"] = "error"
            frame_result["error"] = completed.stderr.strip() or "ffmpeg extraction failed"
        else:
            frame_result["status"] = "ok"
        frames.append(frame_result)
    status = "ok" if all(frame["status"] == "ok" for frame in frames) else "partial"
    return {"status": status, "frames": frames, "output_dir": Path(os.path.relpath(output_dir, SKILL_DIR)).as_posix()}


def build_entry_bundle(entry: dict[str, Any], default_extract: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    missing_sources: list[str] = []
    tool_support = {
        "ffprobe": bool(find_tool("ffprobe")),
        "ffmpeg": bool(find_tool("ffmpeg")),
    }

    metadata_path_value = str(entry.get("metadata_path", "")).strip()
    if metadata_path_value:
        resolved_metadata = resolve_path(metadata_path_value)
        if resolved_metadata.exists():
            loaded = load_json(resolved_metadata)
            if isinstance(loaded, dict):
                metadata.update(loaded)
        else:
            missing_sources.append(f"missing metadata file: {metadata_path_value}")

    video_path_value = str(entry.get("video_path", "")).strip()
    if video_path_value:
        resolved_video = resolve_path(video_path_value)
        metadata["video_exists"] = resolved_video.exists()
        if resolved_video.exists():
            metadata["video_path"] = video_path_value
            probed, probe_error = probe_video(resolved_video)
            metadata.update(probed)
            if probe_error:
                metadata["probe_error"] = probe_error
        else:
            missing_sources.append(f"missing video file: {video_path_value}")

    transcript_segments: list[dict[str, str]] = []
    transcript_path_value = str(entry.get("transcript_path", "")).strip()
    if transcript_path_value:
        resolved_transcript = resolve_path(transcript_path_value)
        if resolved_transcript.exists():
            transcript_segments = parse_transcript(resolved_transcript)
        else:
            missing_sources.append(f"missing transcript file: {transcript_path_value}")

    frame_sections: list[dict[str, Any]] = []
    frame_notes_path_value = str(entry.get("frame_notes_path", "")).strip()
    if frame_notes_path_value:
        resolved_frames = resolve_path(frame_notes_path_value)
        if resolved_frames.exists():
            frame_sections = parse_markdown_sections(resolved_frames)
        else:
            missing_sources.append(f"missing frame notes file: {frame_notes_path_value}")

    review_sections: list[dict[str, Any]] = []
    review_notes_path_value = str(entry.get("review_notes_path", "")).strip()
    if review_notes_path_value:
        resolved_review = resolve_path(review_notes_path_value)
        if resolved_review.exists():
            review_sections = parse_markdown_sections(resolved_review)
        else:
            missing_sources.append(f"missing review notes file: {review_notes_path_value}")

    merged_extract = dict(default_extract)
    merged_extract.update(entry.get("extract", {}) or {})
    extracted_frames = extract_frames({**entry, "extract": merged_extract}, metadata)

    available_sources = 0
    if metadata:
        available_sources += 1
    if transcript_segments:
        available_sources += 1
    if frame_sections or review_sections:
        available_sources += 1
    minimum_sources = int(merged_extract.get("minimum_sources", 2))
    evidence_ready = available_sources >= minimum_sources
    transcript_excerpt = " ".join(segment["text"] for segment in transcript_segments[:5]).strip()
    frame_markers = [
        {
            "heading": section.get("heading", ""),
            "start": section.get("start", ""),
            "end": section.get("end", ""),
            "note": section.get("content", ""),
        }
        for section in frame_sections
    ]
    review_markers = [
        {
            "heading": section.get("heading", ""),
            "start": section.get("start", ""),
            "end": section.get("end", ""),
            "note": section.get("content", ""),
        }
        for section in review_sections
    ]

    return {
        "id": entry.get("id", ""),
        "title": entry.get("title", ""),
        "status": entry.get("status", "pending"),
        "platform": entry.get("platform", ""),
        "metadata": metadata,
        "transcript_segments": transcript_segments,
        "frame_sections": frame_sections,
        "review_sections": review_sections,
        "frame_markers": frame_markers,
        "review_markers": review_markers,
        "extracted_frames": extracted_frames,
        "missing_sources": missing_sources,
        "issues": missing_sources,
        "tool_support": tool_support,
        "evidence_ready": evidence_ready,
        "marker_count": len(frame_markers) + len(review_markers),
        "transcript": {
            "segment_count": len(transcript_segments),
            "excerpt": transcript_excerpt,
            "full_text": "\n".join(
                f"{segment['timestamp']} {segment['text']}".strip()
                for segment in transcript_segments
            ).strip(),
        },
        "review_into": list(entry.get("review_into", [])),
        "source_paths": {
            "video_path": video_path_value,
            "metadata_path": metadata_path_value,
            "transcript_path": transcript_path_value,
            "frame_notes_path": frame_notes_path_value,
            "review_notes_path": review_notes_path_value,
        },
        "counts": {
            "transcript_segments": len(transcript_segments),
            "frame_sections": len(frame_sections),
            "review_sections": len(review_sections),
            "extracted_frames": len(extracted_frames.get("frames", [])),
        },
    }


def build_markdown(summary: dict[str, Any], bundles: list[dict[str, Any]]) -> str:
    lines = [
        "# Video Evidence Bundle",
        "",
        "Generated from `video-evidence-registry.json` by `scripts/build_video_evidence_bundle.py`.",
        "",
        f"- active_entries: {summary['active_entries']}",
        f"- evidence_ready_entries: {summary['evidence_ready_entries']}",
        f"- entries_with_missing_sources: {summary['entries_with_missing_sources']}",
        f"- ffprobe_available: `{summary['ffprobe_available']}`",
        f"- ffmpeg_available: `{summary['ffmpeg_available']}`",
        "",
    ]
    if not bundles:
        lines.append("- No enabled video evidence entries.")
        lines.append("")
        return "\n".join(lines)

    for bundle in bundles:
        lines.extend(
            [
                f"## {bundle['title'] or bundle['id']}",
                "",
                f"- id: `{bundle['id']}`",
                f"- status: `{bundle['status']}`",
                f"- evidence_ready: `{bundle['evidence_ready']}`",
                f"- review_into: {render_targets(bundle['review_into'])}",
                f"- transcript_segments: {bundle['counts']['transcript_segments']}",
                f"- frame_sections: {bundle['counts']['frame_sections']}",
                f"- review_sections: {bundle['counts']['review_sections']}",
                f"- extracted_frames: {bundle['counts']['extracted_frames']}",
            ]
        )
        if bundle["missing_sources"]:
            lines.append("- missing_sources:")
            for item in bundle["missing_sources"]:
                lines.append(f"  - {item}")
        metadata = bundle["metadata"]
        if metadata:
            lines.append("- metadata:")
            for key, value in metadata.items():
                lines.append(f"  - {key}: {value}")
        extracted_frames = bundle["extracted_frames"]
        if extracted_frames.get("status") != "skipped":
            lines.append(f"- frame_extract_status: `{extracted_frames.get('status', 'unknown')}`")
        elif extracted_frames.get("reason"):
            lines.append(f"- frame_extract_status: `skipped` ({extracted_frames['reason']})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    config = load_json(CONFIG_PATH)
    if not config.get("enabled", True):
        summary = {
            "active_entries": 0,
            "evidence_ready_entries": 0,
            "entries_with_missing_sources": 0,
            "ffprobe_available": bool(find_tool("ffprobe")),
            "ffmpeg_available": bool(find_tool("ffmpeg")),
            "status": "disabled",
        }
        payload = {"status": "disabled", "summary": summary, "entries": []}
        markdown = (
            "# Video Evidence Bundle\n\n"
            "Video evidence bundling is disabled in `video-evidence-registry.json`.\n"
        )
        write_json_if_changed(OUTPUT_JSON_PATH, payload, args.check)
        write_text_if_changed(OUTPUT_MD_PATH, markdown, args.check)
        return 0

    selected_ids = set(args.entry)
    entries = [
        entry
        for entry in config.get("entries", [])
        if entry.get("enabled", True) and (not selected_ids or entry.get("id") in selected_ids)
    ]
    default_extract = config.get("default_extract", {}) or {}
    bundles = [build_entry_bundle(entry, default_extract) for entry in entries]
    summary = {
        "active_entries": len(bundles),
        "evidence_ready_entries": sum(1 for bundle in bundles if bundle["evidence_ready"]),
        "entries_with_missing_sources": sum(1 for bundle in bundles if bundle["missing_sources"]),
        "ffprobe_available": bool(find_tool("ffprobe")),
        "ffmpeg_available": bool(find_tool("ffmpeg")),
        "status": "ok",
    }
    payload = {"status": "ok", "summary": summary, "entries": bundles}
    markdown = build_markdown(summary, bundles)
    write_json_if_changed(OUTPUT_JSON_PATH, payload, args.check)
    write_text_if_changed(OUTPUT_MD_PATH, markdown, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
