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
from urllib import request


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
BENCHMARKS_DIR = SKILL_DIR / "benchmarks"
CONFIG_PATH = BENCHMARKS_DIR / "video-review-registry.json"
EVIDENCE_JSON_PATH = BENCHMARKS_DIR / "video-evidence.json"
OUTPUT_MD_PATH = BENCHMARKS_DIR / "video-review.md"
OUTPUT_JSON_PATH = BENCHMARKS_DIR / "video-review.json"

WHITESPACE_RE = re.compile(r"\s+")
VERDICT_RE = re.compile(r"^Final verdict:\s*(pass|fail|uncertain)\s*$", re.IGNORECASE | re.MULTILINE)
CONFIDENCE_RE = re.compile(r"^Confidence:\s*(low|medium|high)\s*$", re.IGNORECASE | re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a structured video review report for generated video outputs."
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


def load_evidence_index() -> dict[str, dict[str, Any]]:
    if not EVIDENCE_JSON_PATH.exists():
        return {}
    payload = load_json(EVIDENCE_JSON_PATH)
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        return {}
    return {
        str(entry.get("id", "")).strip(): entry
        for entry in entries
        if isinstance(entry, dict) and str(entry.get("id", "")).strip()
    }


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


def truncate_text(text: str, max_chars: int) -> str:
    stripped = text.strip()
    if len(stripped) <= max_chars:
        return stripped
    return stripped[: max_chars - 18].rstrip() + "\n...[truncated]"


def find_ffprobe() -> str | None:
    return shutil.which("ffprobe")


def probe_video(path: Path) -> dict[str, Any]:
    ffprobe = find_ffprobe()
    if not ffprobe or not path.exists():
        return {}
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
        return {"probe_error": completed.stderr.strip() or "ffprobe failed"}
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"probe_error": "ffprobe returned invalid JSON"}

    video_stream = next(
        (stream for stream in payload.get("streams", []) if stream.get("codec_type") == "video"),
        {},
    )
    format_info = payload.get("format", {})
    result: dict[str, Any] = {
        "video_path": str(path),
        "duration_seconds": None,
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
    }
    duration_raw = format_info.get("duration") or video_stream.get("duration")
    if duration_raw not in (None, ""):
        try:
            result["duration_seconds"] = round(float(duration_raw), 3)
        except (TypeError, ValueError):
            result["duration_seconds"] = None
    return result


def load_metadata(entry: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    metadata_path = str(entry.get("metadata_path", "")).strip()
    if metadata_path:
        resolved = resolve_path(metadata_path)
        if resolved.exists():
            loaded = load_json(resolved)
            if isinstance(loaded, dict):
                metadata.update(loaded)
        else:
            metadata["metadata_path_error"] = f"missing metadata file: {metadata_path}"

    video_path = str(entry.get("video_path", "")).strip()
    if video_path:
        resolved_video = resolve_path(video_path)
        metadata["video_exists"] = resolved_video.exists()
        if resolved_video.exists():
            metadata.setdefault("video_path", video_path)
            metadata.update(
                {
                    key: value
                    for key, value in probe_video(resolved_video).items()
                    if value not in ("", None)
                }
            )
        else:
            metadata["video_path_error"] = f"missing video file: {video_path}"
    return metadata


def read_optional_text(entry: dict[str, Any], key: str) -> tuple[str, str | None]:
    value = str(entry.get(key, "")).strip()
    if not value:
        return "", None
    resolved = resolve_path(value)
    if not resolved.exists():
        return "", f"missing file: {value}"
    return read_text_flexible(resolved), None


def parse_ratio(value: str) -> float | None:
    spec = value.strip()
    if not spec:
        return None
    if ":" in spec:
        left, right = spec.split(":", 1)
        try:
            return float(left) / float(right)
        except (TypeError, ValueError, ZeroDivisionError):
            return None
    try:
        return float(spec)
    except ValueError:
        return None


def ratio_from_dimensions(width: Any, height: Any) -> float | None:
    try:
        width_value = float(width)
        height_value = float(height)
    except (TypeError, ValueError):
        return None
    if height_value == 0:
        return None
    return width_value / height_value


def make_check(name: str, verdict: str, detail: str, evidence: Any = None) -> dict[str, Any]:
    payload = {
        "name": name,
        "verdict": verdict,
        "detail": detail,
    }
    if evidence is not None:
        payload["evidence"] = evidence
    return payload


def render_markers(markers: list[dict[str, Any]]) -> str:
    if not markers:
        return ""
    rendered: list[str] = []
    for marker in markers[:10]:
        window = ""
        if marker.get("start") and marker.get("end"):
            window = f"{marker['start']} -> {marker['end']}"
        elif marker.get("start"):
            window = str(marker["start"])
        elif marker.get("heading"):
            window = str(marker["heading"])
        else:
            window = "unlabeled"
        note = normalize_text(str(marker.get("note", "")))
        rendered.append(f"- {window}: {note}")
    return "\n".join(rendered)


def contains_phrase(haystack: str, needle: str) -> bool:
    return needle.lower() in haystack.lower()


def evaluate_checks(
    entry: dict[str, Any],
    metadata: dict[str, Any],
    transcript_text: str,
    frame_notes_text: str,
    review_notes_text: str,
) -> list[dict[str, Any]]:
    checks = entry.get("checks", {}) or {}
    results: list[dict[str, Any]] = []
    combined_text = "\n".join(
        part for part in [transcript_text, frame_notes_text, review_notes_text] if part.strip()
    )

    duration_rule = checks.get("duration_seconds", {})
    if duration_rule:
        duration = metadata.get("duration_seconds")
        if duration is None:
            results.append(
                make_check(
                    "duration_seconds",
                    "unknown",
                    "No duration metadata available; provide `metadata_path` or install `ffprobe`.",
                )
            )
        else:
            minimum = duration_rule.get("min")
            maximum = duration_rule.get("max")
            passed = True
            if minimum is not None and duration < float(minimum):
                passed = False
            if maximum is not None and duration > float(maximum):
                passed = False
            detail = f"Duration is {duration}s; expected"
            bounds: list[str] = []
            if minimum is not None:
                bounds.append(f">= {minimum}s")
            if maximum is not None:
                bounds.append(f"<= {maximum}s")
            detail += " " + " and ".join(bounds) if bounds else ""
            results.append(make_check("duration_seconds", "pass" if passed else "fail", detail, duration))

    aspect_ratio = str(checks.get("aspect_ratio", "")).strip()
    if aspect_ratio:
        expected_ratio = parse_ratio(aspect_ratio)
        actual_ratio = ratio_from_dimensions(metadata.get("width"), metadata.get("height"))
        if expected_ratio is None:
            results.append(
                make_check(
                    "aspect_ratio",
                    "unknown",
                    f"Could not parse expected aspect ratio `{aspect_ratio}`.",
                )
            )
        elif actual_ratio is None:
            results.append(
                make_check(
                    "aspect_ratio",
                    "unknown",
                    "No width/height metadata available; provide `metadata_path` or install `ffprobe`.",
                )
            )
        else:
            passed = abs(actual_ratio - expected_ratio) <= 0.03
            detail = (
                f"Actual ratio is {round(actual_ratio, 4)} from "
                f"{metadata.get('width')}x{metadata.get('height')}; expected `{aspect_ratio}`."
            )
            results.append(make_check("aspect_ratio", "pass" if passed else "fail", detail))

    transcript_lower = transcript_text.lower()
    for phrase in checks.get("must_include_transcript", []) or []:
        if not transcript_text.strip():
            verdict = "unknown"
            detail = f"Missing transcript evidence for required phrase `{phrase}`."
        elif contains_phrase(transcript_lower, phrase):
            verdict = "pass"
            detail = f"Transcript contains required phrase `{phrase}`."
        else:
            verdict = "fail"
            detail = f"Transcript does not contain required phrase `{phrase}`."
        results.append(make_check(f"must_include_transcript:{phrase}", verdict, detail))

    for phrase in checks.get("must_exclude_transcript", []) or []:
        if not transcript_text.strip():
            verdict = "unknown"
            detail = f"Missing transcript evidence for excluded phrase `{phrase}`."
        elif contains_phrase(transcript_lower, phrase):
            verdict = "fail"
            detail = f"Transcript contains excluded phrase `{phrase}`."
        else:
            verdict = "pass"
            detail = f"Transcript does not contain excluded phrase `{phrase}`."
        results.append(make_check(f"must_exclude_transcript:{phrase}", verdict, detail))

    combined_lower = combined_text.lower()
    for phrase in checks.get("must_include_evidence", []) or []:
        if not combined_text.strip():
            verdict = "unknown"
            detail = f"Missing text evidence for required item `{phrase}`."
        elif contains_phrase(combined_lower, phrase):
            verdict = "pass"
            detail = f"Evidence contains required item `{phrase}`."
        else:
            verdict = "fail"
            detail = f"Evidence does not contain required item `{phrase}`."
        results.append(make_check(f"must_include_evidence:{phrase}", verdict, detail))

    for phrase in checks.get("must_exclude_evidence", []) or []:
        if not combined_text.strip():
            verdict = "unknown"
            detail = f"Missing text evidence for excluded item `{phrase}`."
        elif contains_phrase(combined_lower, phrase):
            verdict = "fail"
            detail = f"Evidence contains excluded item `{phrase}`."
        else:
            verdict = "pass"
            detail = f"Evidence does not contain excluded item `{phrase}`."
        results.append(make_check(f"must_exclude_evidence:{phrase}", verdict, detail))

    return results


def summarize_heuristics(results: list[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(1 for item in results if item["verdict"] == "pass")
    failed = sum(1 for item in results if item["verdict"] == "fail")
    unknown = sum(1 for item in results if item["verdict"] == "unknown")
    if failed:
        verdict = "fail"
    elif unknown:
        verdict = "uncertain"
    elif results:
        verdict = "pass"
    else:
        verdict = "uncertain"
    return {
        "verdict": verdict,
        "passed_checks": passed,
        "failed_checks": failed,
        "unknown_checks": unknown,
    }


def build_prompt(entry: dict[str, Any], evidence: dict[str, Any], heuristic_summary: dict[str, Any]) -> str:
    acceptance_lines = entry.get("acceptance_criteria", []) or []
    red_flags = entry.get("red_flags", []) or []
    checks = evidence["heuristic_checks"]
    transcript_excerpt = truncate_text(evidence["transcript_text"], int(evidence["max_evidence_chars"]))
    frame_notes_excerpt = truncate_text(evidence["frame_notes_text"], int(evidence["max_evidence_chars"]))
    review_notes_excerpt = truncate_text(evidence["review_notes_text"], int(evidence["max_evidence_chars"]))
    evidence_bundle_excerpt = truncate_text(evidence["bundle_excerpt"], int(evidence["max_evidence_chars"]))
    marker_excerpt = evidence["marker_excerpt"] or "[none]"
    heuristic_lines = [
        f"- {item['name']}: {item['verdict']} | {item['detail']}" for item in checks
    ] or ["- none"]
    metadata = evidence["metadata"]
    metadata_lines = []
    for key in ["duration_seconds", "width", "height", "video_path", "video_exists", "metadata_path_error", "video_path_error", "probe_error"]:
        if key in metadata:
            metadata_lines.append(f"- {key}: {metadata[key]}")
    if not metadata_lines:
        metadata_lines = ["- none"]

    return f"""You are reviewing whether a generated video satisfies its production brief.

Be strict. If the available evidence is insufficient, output `uncertain` instead of `pass`.
Do not pretend you saw visuals that are not supported by the evidence.

Output exactly this structure:
Final verdict: <pass|fail|uncertain>
Confidence: <low|medium|high>
Matched requirements:
- ...
Failed requirements:
- ...
Missing evidence:
- ...
Suggested fixes:
- ...
Knowledge writeback:
- ...

Review target:
- id: {entry.get('id', '')}
- title: {entry.get('title', '')}
- goal: {entry.get('goal', '')}
- status: {entry.get('status', '')}

Acceptance criteria:
{chr(10).join(f"- {line}" for line in acceptance_lines) if acceptance_lines else "- none"}

Red flags:
{chr(10).join(f"- {line}" for line in red_flags) if red_flags else "- none"}

Heuristic summary:
- verdict: {heuristic_summary['verdict']}
- passed_checks: {heuristic_summary['passed_checks']}
- failed_checks: {heuristic_summary['failed_checks']}
- unknown_checks: {heuristic_summary['unknown_checks']}

Heuristic checks:
{chr(10).join(heuristic_lines)}

Metadata:
{chr(10).join(metadata_lines)}

Transcript excerpt:
{transcript_excerpt or "[none]"}

Frame notes excerpt:
{frame_notes_excerpt or "[none]"}

Review notes excerpt:
{review_notes_excerpt or "[none]"}

Evidence bundle excerpt:
{evidence_bundle_excerpt or "[none]"}

Extracted markers:
{marker_excerpt}
"""


def llm_credentials() -> tuple[str, str]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = os.environ.get("VIDEO_REVIEW_MODEL", "").strip()
    return api_key, model


def call_openai_chat(prompt: str, api_key: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You review generated video outputs against production briefs and return strict verdicts.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }
    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with request.urlopen(req, timeout=90) as response:
        data = json.loads(response.read().decode("utf-8"))
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("OpenAI response did not contain choices")
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        return "\n".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") in {None, "text"}
        ).strip()
    return str(content).strip()


def parse_review_fields(text: str) -> tuple[str | None, str | None]:
    verdict_match = VERDICT_RE.search(text)
    confidence_match = CONFIDENCE_RE.search(text)
    verdict = verdict_match.group(1).lower() if verdict_match else None
    confidence = confidence_match.group(1).lower() if confidence_match else None
    return verdict, confidence


def fallback_markdown(prompt: str) -> str:
    return "\n".join(
        [
            "LLM review was skipped because `OPENAI_API_KEY` or `VIDEO_REVIEW_MODEL` is not configured.",
            "",
            "### Manual Review Prompt",
            "",
            "```text",
            prompt,
            "```",
        ]
    )


def build_entry_report(
    entry: dict[str, Any],
    default_review: dict[str, Any],
    evidence_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence_id = str(entry.get("evidence_id", "")).strip() or str(entry.get("id", "")).strip()
    metadata = load_metadata(entry)
    if evidence_bundle:
        metadata = {**metadata, **(evidence_bundle.get("metadata", {}) or {})}
    transcript_text, transcript_error = read_optional_text(entry, "transcript_path")
    frame_notes_text, frame_notes_error = read_optional_text(entry, "frame_notes_path")
    review_notes_text, review_notes_error = read_optional_text(entry, "review_notes_path")
    if evidence_bundle and not transcript_text.strip():
        transcript_text = str((evidence_bundle.get("transcript", {}) or {}).get("full_text", "")).strip()
    if evidence_bundle and not frame_notes_text.strip():
        frame_notes_text = "\n".join(
            normalize_text(str(marker.get("note", "")))
            for marker in list(evidence_bundle.get("frame_markers", []) or [])
            if normalize_text(str(marker.get("note", "")))
        ).strip()
    if evidence_bundle and not review_notes_text.strip():
        review_notes_text = "\n".join(
            normalize_text(str(marker.get("note", "")))
            for marker in list(evidence_bundle.get("review_markers", []) or [])
            if normalize_text(str(marker.get("note", "")))
        ).strip()
    evidence_errors = [
        error for error in [transcript_error, frame_notes_error, review_notes_error] if error
    ]
    if evidence_bundle:
        evidence_errors.extend(evidence_bundle.get("issues", []) or [])
    heuristic_checks = evaluate_checks(
        entry,
        metadata,
        transcript_text,
        frame_notes_text,
        review_notes_text,
    )
    heuristic_summary = summarize_heuristics(heuristic_checks)
    frame_markers = list((evidence_bundle or {}).get("frame_markers", []) or [])
    review_markers = list((evidence_bundle or {}).get("review_markers", []) or [])
    bundle_excerpt = normalize_text(str((evidence_bundle or {}).get("transcript", {}).get("excerpt", "")))
    marker_excerpt = render_markers(frame_markers + review_markers)
    max_evidence_chars = int((entry.get("review") or {}).get("max_evidence_chars", default_review.get("max_evidence_chars", 6000)))
    evidence = {
        "metadata": metadata,
        "transcript_text": transcript_text,
        "frame_notes_text": frame_notes_text,
        "review_notes_text": review_notes_text,
        "bundle_excerpt": bundle_excerpt,
        "marker_excerpt": marker_excerpt,
        "heuristic_checks": heuristic_checks,
        "max_evidence_chars": max_evidence_chars,
    }

    prompt = build_prompt(entry, evidence, heuristic_summary)
    api_key, model = llm_credentials()
    review_status = "skipped"
    review_markdown = fallback_markdown(prompt)
    llm_verdict = None
    llm_confidence = None

    if api_key and model:
        review_markdown = call_openai_chat(prompt, api_key, model)
        llm_verdict, llm_confidence = parse_review_fields(review_markdown)
        review_status = "generated"

    final_verdict = llm_verdict or heuristic_summary["verdict"]
    if evidence_errors and final_verdict == "pass":
        final_verdict = "uncertain"
    if evidence_bundle and not evidence_bundle.get("evidence_ready", False) and final_verdict == "pass":
        final_verdict = "uncertain"

    return {
        "id": entry.get("id", ""),
        "title": entry.get("title", ""),
        "status": entry.get("status", "pending"),
        "goal": entry.get("goal", ""),
        "evidence_id": evidence_id,
        "review_into": list(entry.get("review_into", [])),
        "acceptance_criteria": list(entry.get("acceptance_criteria", [])),
        "red_flags": list(entry.get("red_flags", [])),
        "metadata": metadata,
        "evidence_errors": evidence_errors,
        "evidence_bundle_ready": (evidence_bundle or {}).get("evidence_ready"),
        "evidence_bundle_marker_count": (evidence_bundle or {}).get("marker_count", 0),
        "heuristic_checks": heuristic_checks,
        "heuristic_summary": heuristic_summary,
        "review_status": review_status,
        "review_model": model or None,
        "review_markdown": review_markdown,
        "review_prompt_preview": prompt[:6000],
        "llm_verdict": llm_verdict,
        "llm_confidence": llm_confidence,
        "final_verdict": final_verdict,
        "evidence_paths": {
            "video_path": entry.get("video_path", ""),
            "metadata_path": entry.get("metadata_path", ""),
            "transcript_path": entry.get("transcript_path", ""),
            "frame_notes_path": entry.get("frame_notes_path", ""),
            "review_notes_path": entry.get("review_notes_path", ""),
        },
    }


def build_markdown(summary: dict[str, Any], reports: list[dict[str, Any]]) -> str:
    lines = [
        "# Video Review Report",
        "",
        "Generated from `video-review-registry.json` by `scripts/build_video_review_report.py`.",
        "",
        f"- active_entries: {summary['active_entries']}",
        f"- pass_entries: {summary['pass_entries']}",
        f"- fail_entries: {summary['fail_entries']}",
        f"- uncertain_entries: {summary['uncertain_entries']}",
        f"- llm_generated_entries: {summary['llm_generated_entries']}",
        "",
    ]
    if not reports:
        lines.append("- No enabled video review entries.")
        lines.append("")
        return "\n".join(lines)

    for report in reports:
        lines.extend(
            [
                f"## {report['title'] or report['id']}",
                "",
                f"- id: `{report['id']}`",
                f"- status: `{report['status']}`",
                f"- final_verdict: `{report['final_verdict']}`",
                f"- heuristic_verdict: `{report['heuristic_summary']['verdict']}`",
                f"- review_status: `{report['review_status']}`",
                f"- evidence_id: `{report['evidence_id']}`",
                f"- evidence_bundle_ready: `{report['evidence_bundle_ready']}`",
                f"- evidence_bundle_marker_count: {report['evidence_bundle_marker_count']}",
                f"- review_into: {render_targets(report['review_into'])}",
            ]
        )
        if report["goal"]:
            lines.append(f"- goal: {report['goal']}")
        if report["acceptance_criteria"]:
            lines.append("- acceptance_criteria:")
            for item in report["acceptance_criteria"]:
                lines.append(f"  - {item}")
        if report["red_flags"]:
            lines.append("- red_flags:")
            for item in report["red_flags"]:
                lines.append(f"  - {item}")
        metadata = report["metadata"]
        if metadata:
            lines.append("- metadata:")
            for key, value in metadata.items():
                lines.append(f"  - {key}: {value}")
        if report["evidence_errors"]:
            lines.append("- evidence_errors:")
            for error in report["evidence_errors"]:
                lines.append(f"  - {error}")
        lines.append("- heuristic_checks:")
        for item in report["heuristic_checks"]:
            lines.append(f"  - `{item['verdict']}` {item['name']} -> {item['detail']}")
        lines.extend(["", "### Review", "", report["review_markdown"].strip(), ""])

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    config = load_json(CONFIG_PATH)
    if not config.get("enabled", True):
        summary = {
            "active_entries": 0,
            "pass_entries": 0,
            "fail_entries": 0,
            "uncertain_entries": 0,
            "llm_generated_entries": 0,
            "status": "disabled",
        }
        payload = {"status": "disabled", "summary": summary, "entries": []}
        markdown = (
            "# Video Review Report\n\n"
            "Video review is disabled in `video-review-registry.json`.\n"
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
    default_review = config.get("default_review", {}) or {}
    evidence_index = load_evidence_index()
    reports = [
        build_entry_report(
            entry,
            default_review,
            evidence_index.get(str(entry.get("evidence_id", "")).strip() or str(entry.get("id", "")).strip()),
        )
        for entry in entries
    ]

    summary = {
        "active_entries": len(reports),
        "pass_entries": sum(1 for report in reports if report["final_verdict"] == "pass"),
        "fail_entries": sum(1 for report in reports if report["final_verdict"] == "fail"),
        "uncertain_entries": sum(1 for report in reports if report["final_verdict"] == "uncertain"),
        "llm_generated_entries": sum(1 for report in reports if report["review_status"] == "generated"),
        "status": "ok",
    }
    payload = {
        "status": "ok",
        "summary": summary,
        "entries": reports,
    }
    markdown = build_markdown(summary, reports)
    write_json_if_changed(OUTPUT_JSON_PATH, payload, args.check)
    write_text_if_changed(OUTPUT_MD_PATH, markdown, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
