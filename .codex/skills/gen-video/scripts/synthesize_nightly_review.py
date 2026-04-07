#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib import request


SCRIPT_PATH = Path(__file__).resolve()
SKILL_DIR = SCRIPT_PATH.parent.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
NIGHTLY_REVIEW_MD_PATH = KNOWLEDGE_DIR / "nightly-review.md"
NIGHTLY_REVIEW_JSON_PATH = KNOWLEDGE_DIR / "nightly-review.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.md"
OUTPUT_MD_PATH = KNOWLEDGE_DIR / "nightly-review-llm.md"
OUTPUT_JSON_PATH = KNOWLEDGE_DIR / "nightly-review-llm.json"

AUTO_BLOCK_START = "<!-- AUTO:NIGHTLY-LLM:START -->"
AUTO_BLOCK_END = "<!-- AUTO:NIGHTLY-LLM:END -->"
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synthesize the nightly knowledge review into an LLM-style review brief."
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


def load_context() -> dict[str, str]:
    files = {
        "nightly_review_md": NIGHTLY_REVIEW_MD_PATH.read_text(encoding="utf-8"),
        "nightly_review_json": NIGHTLY_REVIEW_JSON_PATH.read_text(encoding="utf-8"),
        "knowledge_index": (KNOWLEDGE_DIR / "index.md").read_text(encoding="utf-8"),
        "knowledge_status": (KNOWLEDGE_DIR / "status.md").read_text(encoding="utf-8"),
        "knowledge_candidates": (KNOWLEDGE_DIR / "candidates.md").read_text(encoding="utf-8"),
        "knowledge_suggestions": (KNOWLEDGE_DIR / "suggestions.md").read_text(encoding="utf-8"),
        "karpathy_gap": (KNOWLEDGE_DIR / "wiki" / "concepts" / "karpathy-gap-analysis.md").read_text(encoding="utf-8"),
    }
    return files


def sanitize_markdown_links(text: str) -> str:
    return LINK_RE.sub(lambda match: f"{match.group(1)} <{match.group(2)}>", text)


def build_prompt(context: dict[str, str]) -> str:
    safe_context = {key: sanitize_markdown_links(value) for key, value in context.items()}
    return f"""You are reviewing a nightly knowledge intelligence packet for the gen-video skill.

Goal:
1. Compare nightly discoveries against current knowledge.
2. Identify what is genuinely new, what overlaps with existing knowledge, and what should be admitted, deferred, or rejected.
3. Produce a human review brief, not an auto-merge decision.

Output structure:
- Executive Summary
- Highest-Signal New Items
- Conflicts Or Gaps Against Existing Knowledge
- Recommended Actions
- Final Human Gate

Current context follows.

## Nightly Review
{safe_context['nightly_review_md']}

## Knowledge Index
{safe_context['knowledge_index']}

## Status
{safe_context['knowledge_status']}

## Candidates
{safe_context['knowledge_candidates']}

## Suggestions
{safe_context['knowledge_suggestions']}

## Karpathy Gap
{safe_context['karpathy_gap']}
"""


def llm_credentials() -> tuple[str, str]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = os.environ.get("KNOWLEDGE_REVIEW_MODEL", "").strip()
    return api_key, model


def call_openai_chat(prompt: str, api_key: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You write concise, high-signal nightly review memos for human approval gates.",
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


def fallback_markdown(prompt: str) -> str:
    return "\n".join(
        [
            "# Nightly LLM Review",
            "",
            "LLM synthesis was skipped because `OPENAI_API_KEY` or `KNOWLEDGE_REVIEW_MODEL` is not configured.",
            "",
            "## Manual Review Prompt",
            "",
            "```text",
            prompt,
            "```",
            "",
        ]
    )


def build_index_block(status: str) -> str:
    lines = [
        AUTO_BLOCK_START,
        f"- [nightly-review-llm.md](nightly-review-llm.md) is the synthesized review brief for the nightly intelligence packet.",
        f"- LLM synthesis status: `{status}`",
        AUTO_BLOCK_END,
    ]
    return "\n".join(lines)


def update_index(status: str, check: bool) -> bool:
    current = INDEX_PATH.read_text(encoding="utf-8")
    block = build_index_block(status)
    if AUTO_BLOCK_START in current and AUTO_BLOCK_END in current:
        before, remainder = current.split(AUTO_BLOCK_START, 1)
        _, after = remainder.split(AUTO_BLOCK_END, 1)
        updated = before.rstrip() + "\n\n" + block + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    return write_text_if_changed(INDEX_PATH, updated, check)


def main() -> int:
    args = parse_args()
    context = load_context()
    prompt = build_prompt(context)
    api_key, model = llm_credentials()

    if api_key and model:
        review = call_openai_chat(prompt, api_key, model)
        status = "generated"
        payload = {
            "status": status,
            "model": model,
            "review": review,
        }
        markdown = "# Nightly LLM Review\n\n" + review.strip() + "\n"
    else:
        status = "skipped"
        payload = {
            "status": status,
            "model": model or None,
            "review": None,
            "prompt_preview": prompt[:4000],
        }
        markdown = fallback_markdown(prompt)

    write_json_if_changed(OUTPUT_JSON_PATH, payload, args.check)
    write_text_if_changed(OUTPUT_MD_PATH, markdown, args.check)
    update_index(status, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
