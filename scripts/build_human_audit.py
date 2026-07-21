"""Build a reproducible human-review sample from completed Inspect logs.

The default audit contains 20 successful outputs:
  * 10 R6 J&K and 10 R7 taxon samples
  * two examples of every condition in each arm
  * five examples from every model across the full audit

All parse failures from the selected full runs are appended as mandatory
exception reviews and do not count toward the 20-sample random audit.

Usage:
    python scripts/build_human_audit.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from inspect_ai.log import list_eval_logs, read_eval_log

from src.schema import canonical_model_id, parse_ci_triple

SCORER_NAME = "anchored_ci_scorer"
ARMS = {"jk": ("R6 J&K", 75), "taxon": ("R7 taxon", 90)}
MODELS = (
    "claude-sonnet-4-5-20250929",
    "claude-haiku-4-5-20251001",
    "gpt-4o",
    "gpt-4o-mini",
)
MODEL_LABELS = {
    "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
    "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
    "gpt-4o": "GPT-4o",
    "gpt-4o-mini": "GPT-4o mini",
}
CONDITIONS = ("control", "low_arb", "high_arb", "low_plaus", "high_plaus")

# Two models per condition in each arm. Across both arms, every model appears
# exactly five times.
MODEL_PAIRS = {
    "jk": ((0, 1), (2, 3), (0, 2), (1, 3), (0, 3)),
    "taxon": ((1, 2), (3, 0), (1, 3), (2, 0), (1, 2)),
}


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            str(getattr(part, "text", getattr(part, "content", part)))
            for part in content
        )
    return str(content)


def _discover_full_logs(log_dir: str) -> dict[tuple[str, str], tuple[str, Any]]:
    selected: dict[tuple[str, str], tuple[str, Any]] = {}
    for info in list_eval_logs(log_dir, descending=True):
        log = read_eval_log(info)
        item_set = log.eval.metadata.get("item_set")
        if item_set not in ARMS or log.status != "success":
            continue
        model = canonical_model_id(log.eval.model)
        key = (item_set, model)
        if model not in MODELS or key in selected:
            continue
        expected_samples = ARMS[item_set][1]
        if len(log.samples or []) != expected_samples:
            continue
        selected[key] = (info.name, log)

    missing = [
        f"{arm}/{model}"
        for arm in ARMS
        for model in MODELS
        if (arm, model) not in selected
    ]
    if missing:
        raise FileNotFoundError(
            "could not find full successful logs for: " + ", ".join(missing)
        )
    return selected


def _record(
    *,
    audit_id: str,
    arm: str,
    model: str,
    log_path: str,
    sample: Any,
    exception: bool,
) -> dict[str, Any]:
    score = (sample.scores or {}).get(SCORER_NAME)
    if score is None:
        raise ValueError(f"{log_path} sample {sample.id} has no {SCORER_NAME} score")
    metadata = score.metadata or {}
    raw_completion = sample.output.completion
    fresh_reparse = parse_ci_triple(raw_completion)
    scorer_triple = (
        metadata.get("lower"),
        metadata.get("point"),
        metadata.get("upper"),
    )
    scorer_parsed = bool(score.value)
    parser_agrees = (
        scorer_triple == fresh_reparse
        if fresh_reparse is not None
        else not scorer_parsed
    )
    transcript = [
        {"role": message.role, "content": _message_text(message.content)}
        for message in sample.messages
    ]
    return {
        "audit_id": audit_id,
        "exception": exception,
        "arm": ARMS[arm][0],
        "item_set": arm,
        "model": MODEL_LABELS[model],
        "model_id": model,
        "source_log": log_path,
        "sample_id": str(sample.id),
        "sample_uuid": str(sample.uuid),
        "item_id": metadata.get("item_id"),
        "condition": metadata.get("condition"),
        "anchor": metadata.get("anchor"),
        "provenance": metadata.get("provenance"),
        "direction": metadata.get("direction"),
        "raw_completion": raw_completion,
        "completion_sha256": hashlib.sha256(
            raw_completion.encode("utf-8")
        ).hexdigest(),
        "comparative_answer": metadata.get("comparative_answer"),
        "control_acknowledgement": metadata.get("control_acknowledgement"),
        "scorer_parsed": scorer_parsed,
        "scorer_lower": metadata.get("lower"),
        "scorer_point": metadata.get("point"),
        "scorer_upper": metadata.get("upper"),
        "scorer_relative_width": metadata.get("value"),
        "fresh_reparse": list(fresh_reparse) if fresh_reparse else None,
        "automatic_reparse_agreement": parser_agrees,
        "score_explanation": score.explanation,
        "transcript": transcript,
        "human_review": {
            "raw_response_matches_log": None,
            "parsed_values_correct": None,
            "metadata_matches_prompt": None,
            "first_turn_recorded_correctly": None,
            "verdict": "pending",
            "reviewer": "",
            "reviewed_at": "",
            "notes": "",
        },
    }


def build_audit(log_dir: str, seed: int) -> dict[str, Any]:
    logs = _discover_full_logs(log_dir)
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []

    for arm, pairs in MODEL_PAIRS.items():
        for condition, pair in zip(CONDITIONS, pairs, strict=True):
            for model_index in pair:
                model = MODELS[model_index]
                log_path, log = logs[(arm, model)]
                candidates = [
                    sample
                    for sample in log.samples or []
                    if sample.metadata.get("condition") == condition
                    and bool((sample.scores or {})[SCORER_NAME].value)
                ]
                sample = rng.choice(sorted(candidates, key=lambda value: str(value.id)))
                records.append(
                    _record(
                        audit_id=f"A{len(records) + 1:02d}",
                        arm=arm,
                        model=model,
                        log_path=log_path,
                        sample=sample,
                        exception=False,
                    )
                )

    exceptions: list[dict[str, Any]] = []
    for (arm, model), (log_path, log) in sorted(logs.items()):
        for sample in log.samples or []:
            score = (sample.scores or {}).get(SCORER_NAME)
            if score is not None and not bool(score.value):
                exceptions.append(
                    _record(
                        audit_id=f"E{len(exceptions) + 1:02d}",
                        arm=arm,
                        model=model,
                        log_path=log_path,
                        sample=sample,
                        exception=True,
                    )
                )

    counts = defaultdict(int)
    for record in records:
        counts[f"arm:{record['item_set']}"] += 1
        counts[f"model:{record['model_id']}"] += 1
        counts[f"condition:{record['item_set']}:{record['condition']}"] += 1

    return {
        "audit_version": 1,
        "selection_seed": seed,
        "selection_method": (
            "Fixed arm/condition/model strata; seeded random item within each stratum"
        ),
        "sample_count": len(records),
        "exception_count": len(exceptions),
        "stratum_counts": dict(sorted(counts.items())),
        "records": records,
        "mandatory_exceptions": exceptions,
    }


def _transcript_markdown(record: dict[str, Any]) -> str:
    lines: list[str] = []
    for message in record["transcript"]:
        lines.extend(
            [
                f"**{message['role'].upper()}**",
                "```text",
                message["content"],
                "```",
            ]
        )
    return "\n".join(lines)


def _record_markdown(record: dict[str, Any]) -> str:
    parsed = (
        f"{record['scorer_lower']} / {record['scorer_point']} / "
        f"{record['scorer_upper']}"
        if record["scorer_parsed"]
        else "REJECTED"
    )
    return "\n".join(
        [
            f"## {record['audit_id']} — {record['arm']} — {record['model']}",
            "",
            f"- Item: `{record['item_id']}`",
            f"- Condition: `{record['condition']}`",
            f"- Anchor: `{record['anchor']}`",
            f"- Source sample: `{record['sample_id']}`",
            f"- Scorer result: **{parsed}**",
            f"- Fresh reparse from raw output: `{record['fresh_reparse']}`",
            f"- Stored score matches fresh reparse: "
            f"`{record['automatic_reparse_agreement']}`",
            "",
            "### Raw transcript",
            "",
            _transcript_markdown(record),
            "",
            "### Human verification",
            "",
            "- [ ] Raw response matches the source transcript",
            "- [ ] Parsed p10/p50/p90 values are correct",
            "- [ ] Condition, anchor, and provenance match the prompt",
            "- [ ] First-turn response or control acknowledgement is recorded correctly",
            "- Verdict: `pending`",
            "- Reviewer:",
            "- Reviewed at:",
            "- Notes:",
            "",
        ]
    )


def render_markdown(audit: dict[str, Any]) -> str:
    sections = [
        "# Human translation audit",
        "",
        f"Selection seed: `{audit['selection_seed']}`  ",
        f"Random audit records: **{audit['sample_count']}**  ",
        f"Mandatory parser exceptions: **{audit['exception_count']}**",
        "",
        "Review every checkbox against the raw transcript. Do not mark the audit",
        "complete until all 20 sampled records and all mandatory exceptions have",
        "a named reviewer, timestamp, verdict, and any discrepancy notes.",
        "",
        "# Stratified random sample",
        "",
    ]
    sections.extend(_record_markdown(record) for record in audit["records"])
    if audit["mandatory_exceptions"]:
        sections.extend(
            [
                "# Mandatory exception review",
                "",
                "These records failed automatic parsing and are reviewed in addition",
                "to the 20-record random sample.",
                "",
            ]
        )
        sections.extend(
            _record_markdown(record) for record in audit["mandatory_exceptions"]
        )
    return "\n".join(sections).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--seed", type=int, default=20260721)
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=Path("results/human_audit_2026-07-21"),
    )
    args = parser.parse_args()

    audit = build_audit(args.log_dir, args.seed)
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = args.output_prefix.with_suffix(".json")
    markdown_path = args.output_prefix.with_suffix(".md")
    json_path.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(audit), encoding="utf-8")
    print(
        f"Wrote {audit['sample_count']} audit records and "
        f"{audit['exception_count']} exceptions to {json_path} and {markdown_path}"
    )


if __name__ == "__main__":
    main()
