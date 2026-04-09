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
BENCHMARKS_DIR = SKILL_DIR / "benchmarks"
REVIEW_JSON_PATH = BENCHMARKS_DIR / "video-review.json"
OUTPUT_MD_PATH = BENCHMARKS_DIR / "video-review-actions.md"
OUTPUT_JSON_PATH = BENCHMARKS_DIR / "video-review-actions.json"

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
SECTION_KEYS = {
    "Matched requirements": "matched_requirements",
    "Failed requirements": "failed_requirements",
    "Missing evidence": "missing_evidence",
    "Suggested fixes": "suggested_fixes",
    "Knowledge writeback": "knowledge_writeback",
}


@dataclass
class ReviewAction:
    action_id: str
    title: str
    priority: str
    final_verdict: str
    action_type: str
    action_summary: str
    queue_status: str
    evidence_id: str
    review_status: str
    llm_confidence: str | None
    rerun_scope: str
    act_targets: list[str]
    evidence_files: list[str]
    matched_requirements: list[str]
    failed_requirements: list[str]
    missing_evidence: list[str]
    suggested_fixes: list[str]
    knowledge_writeback: list[str]
    blocking_issues: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a PDCA Act queue from structured video review results."
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


def dedupe_targets(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def parse_review_sections(markdown: str) -> dict[str, list[str]]:
    parsed = {key: [] for key in SECTION_KEYS.values()}
    current_key: str | None = None
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":") and line[:-1] in SECTION_KEYS:
            current_key = SECTION_KEYS[line[:-1]]
            continue
        if current_key and line.startswith(("- ", "* ")):
            parsed[current_key].append(line[2:].strip())
            continue
        if line.startswith("Final verdict:") or line.startswith("Confidence:"):
            current_key = None
            continue
        if current_key and not line.startswith(("- ", "* ")):
            current_key = None
    return parsed


def collect_heuristic_details(report: dict[str, Any], verdict: str) -> list[str]:
    items: list[str] = []
    for check in report.get("heuristic_checks", []):
        if check.get("verdict") == verdict:
            detail = str(check.get("detail", "")).strip()
            if detail:
                items.append(detail)
    return items


def build_default_suggested_fixes(
    report: dict[str, Any],
    failed_requirements: list[str],
    missing_evidence: list[str],
) -> list[str]:
    final_verdict = str(report.get("final_verdict", "uncertain"))
    marker_count = int(report.get("evidence_bundle_marker_count", 0) or 0)
    fixes: list[str] = []
    if final_verdict == "fail":
        if marker_count > 0:
            fixes.append("优先按 marker 只重做失败镜头，不要整条片盲目重跑。")
        else:
            fixes.append("先在 `review.md` 里补失败镜头定位，再决定局部重做还是整体重做。")
        if failed_requirements:
            fixes.append("对照失败要求回看 brief，先修最硬性的目标漂移、剧情缺失或平台不合规项。")
    elif final_verdict == "uncertain":
        fixes.append("先补齐缺失证据，再重新跑 `evidence -> review -> act` 三步。")
        if not missing_evidence:
            fixes.append("如果证据表面齐全但仍判不清，补更细的 `frames.md` 或人工审片笔记。")
    else:
        fixes.append("保留当前证据基线，并把通过结论写回 benchmark 或知识日志。")
    return fixes


def build_default_writeback(report: dict[str, Any]) -> list[str]:
    review_into = [str(item).strip() for item in report.get("review_into", []) if str(item).strip()]
    final_verdict = str(report.get("final_verdict", "uncertain"))
    actions: list[str] = []
    if final_verdict == "pass":
        if "knowledge/log.md" in review_into:
            actions.append("把本次通过案例记入 `knowledge/log.md`，保留通过条件和证据基线。")
        other_targets = [target for target in review_into if target != "knowledge/log.md"]
        if other_targets:
            actions.append(
                "确认下游目标是否需要吸收这次通过样例："
                + ", ".join(f"`{target}`" for target in other_targets)
            )
    elif final_verdict == "fail":
        actions.append("如果失败模式具有重复性，把失败原因写回 benchmark 或 profile，避免下次继续踩同一类坑。")
    else:
        actions.append("先补证据，再决定这条样例是否值得写回长期知识。")
    return actions


def build_act_targets(
    report: dict[str, Any],
    missing_evidence: list[str],
    knowledge_writeback: list[str],
) -> list[str]:
    targets = [str(item).strip() for item in report.get("review_into", []) if str(item).strip()]
    final_verdict = str(report.get("final_verdict", "uncertain"))
    if final_verdict == "fail":
        targets.extend(
            [
                "benchmarks/video-review-registry.json",
                "benchmarks/output-review-template.md",
            ]
        )
    if final_verdict == "uncertain" or missing_evidence:
        targets.append("benchmarks/video-evidence-registry.json")
    if (
        final_verdict == "pass"
        and knowledge_writeback
        and not any(target.startswith("knowledge/") for target in targets)
    ):
        targets.append("knowledge/log.md")
    return dedupe_targets(targets)


def build_evidence_files(report: dict[str, Any]) -> list[str]:
    evidence_paths = report.get("evidence_paths", {}) or {}
    raw_paths = [
        str(evidence_paths.get("video_path", "")).strip(),
        str(evidence_paths.get("metadata_path", "")).strip(),
        str(evidence_paths.get("transcript_path", "")).strip(),
        str(evidence_paths.get("frame_notes_path", "")).strip(),
        str(evidence_paths.get("review_notes_path", "")).strip(),
    ]
    return dedupe_targets(
        [
            "benchmarks/video-review.md",
            "benchmarks/video-review.json",
            "benchmarks/video-review-actions.md",
            *raw_paths,
        ]
    )


def classify_action(report: dict[str, Any]) -> ReviewAction:
    parsed_sections = parse_review_sections(str(report.get("review_markdown", "")))
    matched_requirements = parsed_sections["matched_requirements"] or list(
        report.get("acceptance_criteria", [])
    )
    failed_requirements = dedupe_targets(
        parsed_sections["failed_requirements"] + collect_heuristic_details(report, "fail")
    )
    missing_evidence = dedupe_targets(
        parsed_sections["missing_evidence"]
        + list(report.get("evidence_errors", []))
        + collect_heuristic_details(report, "unknown")
    )
    suggested_fixes = dedupe_targets(
        parsed_sections["suggested_fixes"]
        + build_default_suggested_fixes(report, failed_requirements, missing_evidence)
    )
    knowledge_writeback = dedupe_targets(
        parsed_sections["knowledge_writeback"] + build_default_writeback(report)
    )

    final_verdict = str(report.get("final_verdict", "uncertain")).strip() or "uncertain"
    marker_count = int(report.get("evidence_bundle_marker_count", 0) or 0)
    if final_verdict == "fail":
        action_type = "rerun-broken-shots"
        priority = "high"
        rerun_scope = "targeted-shot-rerun" if marker_count > 0 else "manual-localization-then-rerun"
        action_summary = "视频未通过审片，先定位失败镜头并局部重做，再重新走一轮审片。"
    elif final_verdict == "uncertain":
        action_type = "collect-missing-evidence"
        priority = "high"
        rerun_scope = "collect-evidence-then-review"
        action_summary = "当前证据不足以稳定判定通过与否，先补证据，再重新审片。"
    else:
        action_type = "writeback-accepted-benchmark"
        priority = "medium"
        rerun_scope = "no-rerun-needed"
        action_summary = "视频已通过当前审片，应把通过样例沉淀成可复用的 benchmark 基线。"

    act_targets = build_act_targets(report, missing_evidence, knowledge_writeback)
    blocking_issues = dedupe_targets(failed_requirements + missing_evidence)[:8]
    return ReviewAction(
        action_id=str(report.get("id", "")),
        title=str(report.get("title", "")).strip(),
        priority=priority,
        final_verdict=final_verdict,
        action_type=action_type,
        action_summary=action_summary,
        queue_status="pending",
        evidence_id=str(report.get("evidence_id", "")).strip(),
        review_status=str(report.get("review_status", "")).strip(),
        llm_confidence=report.get("llm_confidence"),
        rerun_scope=rerun_scope,
        act_targets=act_targets,
        evidence_files=build_evidence_files(report),
        matched_requirements=dedupe_targets(matched_requirements),
        failed_requirements=failed_requirements,
        missing_evidence=missing_evidence,
        suggested_fixes=suggested_fixes,
        knowledge_writeback=knowledge_writeback,
        blocking_issues=blocking_issues,
    )


def build_payload(actions: list[ReviewAction], review_status: str) -> dict[str, Any]:
    return {
        "status": review_status,
        "summary": {
            "total_actions": len(actions),
            "high_priority_actions": sum(1 for action in actions if action.priority == "high"),
            "medium_priority_actions": sum(1 for action in actions if action.priority == "medium"),
            "low_priority_actions": sum(1 for action in actions if action.priority == "low"),
            "fail_actions": sum(1 for action in actions if action.final_verdict == "fail"),
            "uncertain_actions": sum(1 for action in actions if action.final_verdict == "uncertain"),
            "pass_actions": sum(1 for action in actions if action.final_verdict == "pass"),
        },
        "actions": [
            {
                "id": action.action_id,
                "title": action.title,
                "priority": action.priority,
                "final_verdict": action.final_verdict,
                "action_type": action.action_type,
                "action_summary": action.action_summary,
                "queue_status": action.queue_status,
                "evidence_id": action.evidence_id,
                "review_status": action.review_status,
                "llm_confidence": action.llm_confidence,
                "rerun_scope": action.rerun_scope,
                "act_targets": action.act_targets,
                "evidence_files": action.evidence_files,
                "matched_requirements": action.matched_requirements,
                "failed_requirements": action.failed_requirements,
                "missing_evidence": action.missing_evidence,
                "suggested_fixes": action.suggested_fixes,
                "knowledge_writeback": action.knowledge_writeback,
                "blocking_issues": action.blocking_issues,
            }
            for action in actions
        ],
    }


def render_markdown(actions: list[ReviewAction], review_status: str) -> str:
    lines = [
        "# Video Review Action Queue",
        "",
        "Generated from `video-review.json` by `scripts/build_video_review_action_queue.py`.",
        "",
        f"- review_status: `{review_status}`",
        f"- total_actions: {len(actions)}",
        f"- high_priority_actions: {sum(1 for action in actions if action.priority == 'high')}",
        f"- medium_priority_actions: {sum(1 for action in actions if action.priority == 'medium')}",
        f"- low_priority_actions: {sum(1 for action in actions if action.priority == 'low')}",
        "",
    ]
    if not actions:
        lines.append("- No reviewed video entries produced follow-up actions in the latest run.")
        lines.append("")
        return "\n".join(lines)

    for priority in ("high", "medium", "low"):
        group = [action for action in actions if action.priority == priority]
        lines.extend([f"## {priority.title()} Priority", ""])
        if not group:
            lines.append("- None.")
            lines.append("")
            continue
        for action in group:
            lines.extend(
                [
                    f"### {action.title or action.action_id}",
                    "",
                    f"- id: `{action.action_id}`",
                    f"- final_verdict: `{action.final_verdict}`",
                    f"- action_type: `{action.action_type}`",
                    f"- queue_status: `{action.queue_status}`",
                    f"- review_status: `{action.review_status}`",
                    f"- llm_confidence: `{action.llm_confidence or 'n/a'}`",
                    f"- evidence_id: `{action.evidence_id or action.action_id}`",
                    f"- rerun_scope: `{action.rerun_scope}`",
                    f"- action_summary: {action.action_summary}",
                    f"- act_targets: {render_targets(action.act_targets)}",
                    f"- evidence_files: {render_targets(action.evidence_files)}",
                ]
            )
            if action.blocking_issues:
                lines.append("- blocking_issues:")
                for item in action.blocking_issues:
                    lines.append(f"  - {item}")
            if action.matched_requirements:
                lines.append("- matched_requirements:")
                for item in action.matched_requirements:
                    lines.append(f"  - {item}")
            if action.failed_requirements:
                lines.append("- failed_requirements:")
                for item in action.failed_requirements:
                    lines.append(f"  - {item}")
            if action.missing_evidence:
                lines.append("- missing_evidence:")
                for item in action.missing_evidence:
                    lines.append(f"  - {item}")
            if action.suggested_fixes:
                lines.append("- suggested_fixes:")
                for item in action.suggested_fixes:
                    lines.append(f"  - {item}")
            if action.knowledge_writeback:
                lines.append("- knowledge_writeback:")
                for item in action.knowledge_writeback:
                    lines.append(f"  - {item}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    if not REVIEW_JSON_PATH.exists():
        raise RuntimeError(
            "video-review.json does not exist; run `scripts/build_video_review_report.py` first."
        )

    review_payload = load_json(REVIEW_JSON_PATH)
    review_status = str(review_payload.get("status", "ok"))
    if review_status != "ok":
        payload = build_payload([], review_status)
        markdown = (
            "# Video Review Action Queue\n\n"
            "Video review actions are unavailable because `video-review.json` is not in an `ok` state.\n"
        )
        write_json_if_changed(OUTPUT_JSON_PATH, payload, args.check)
        write_text_if_changed(OUTPUT_MD_PATH, markdown, args.check)
        return 0

    entries = review_payload.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("video-review.json must contain an entries array")

    actions = [classify_action(entry) for entry in entries if isinstance(entry, dict)]
    actions.sort(
        key=lambda action: (
            PRIORITY_ORDER.get(action.priority, 99),
            action.final_verdict,
            (action.title or action.action_id).lower(),
        )
    )
    payload = build_payload(actions, review_status)
    markdown = render_markdown(actions, review_status)
    write_json_if_changed(OUTPUT_JSON_PATH, payload, args.check)
    write_text_if_changed(OUTPUT_MD_PATH, markdown, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
