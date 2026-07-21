"""Summarize a completed J&K anchoring eval log.

Usage:
    python scripts/analyze_jk.py
    python scripts/analyze_jk.py logs/run.eval --output results/summary.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from inspect_ai.log import list_eval_logs, read_eval_log

from src.anchoring_metrics import anchoring_index, width_delta

SCORER_NAME = "anchored_ci_scorer"
PROVENANCES = ("arb", "plaus")


def _latest_jk_log(log_dir: str = "logs") -> str:
    for info in list_eval_logs(log_dir, descending=True):
        header = read_eval_log(info, header_only=True)
        if (
            header.status == "success"
            and header.eval.task == "elicit_anchored"
            and header.eval.metadata.get("item_set") == "jk"
        ):
            return info.name
    raise FileNotFoundError(f"no successful J&K eval logs found under {log_dir!r}")


def rows_from_log(path: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    log = read_eval_log(path)
    rows: list[dict[str, Any]] = []
    for sample in log.samples or []:
        score = (sample.scores or {}).get(SCORER_NAME)
        if score is None:
            continue
        metadata = score.metadata or {}
        rows.append(
            {
                **metadata,
                "parsed": bool(score.value),
                "completion": sample.output.completion,
            }
        )
    run = {
        "log": path,
        "model": log.eval.model,
        "created": log.eval.created,
        "samples": len(rows),
    }
    return rows, run


def _finite(values: list[float | None]) -> list[float]:
    return [
        float(value)
        for value in values
        if value is not None and math.isfinite(float(value))
    ]


def _median_field(rows: list[dict[str, Any]], field: str) -> float | None:
    values = _finite([row.get(field) for row in rows if row.get("parsed")])
    return median(values) if values else None


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    x_ranks = _ranks(xs)
    y_ranks = _ranks(ys)
    value = float(np.corrcoef(x_ranks, y_ranks)[0, 1])
    return value if math.isfinite(value) else None


def _ranks(values: list[float]) -> np.ndarray:
    """Return average ranks, including correct handling of ties."""
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        average_rank = (start + end - 1) / 2 + 1
        for index in order[start:end]:
            ranks[index] = average_rank
        start = end
    return ranks


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("item_id")), str(row.get("condition")))].append(row)

    parse_rate = sum(bool(row.get("parsed")) for row in rows) / len(rows) if rows else 0.0
    provenance_summaries: dict[str, Any] = {}
    all_comparisons = 0
    consistent_comparisons = 0

    for provenance in PROVENANCES:
        item_ais: list[float] = []
        valid_baseline_ais: list[float] = []
        correlated_item_ais: list[float] = []
        human_ais: list[float] = []
        width_deltas: list[float] = []

        item_ids = sorted({str(row.get("item_id")) for row in rows})
        for item_id in item_ids:
            control_rows = grouped[(item_id, "control")]
            low_rows = grouped[(item_id, f"low_{provenance}")]
            high_rows = grouped[(item_id, f"high_{provenance}")]
            control_point = _median_field(control_rows, "point")
            control_width = _median_field(control_rows, "value")
            low_point = _median_field(low_rows, "point")
            high_point = _median_field(high_rows, "point")

            low_anchor_values = _finite([row.get("anchor") for row in low_rows])
            high_anchor_values = _finite([row.get("anchor") for row in high_rows])
            if (
                low_point is not None
                and high_point is not None
                and low_anchor_values
                and high_anchor_values
            ):
                low_anchor = median(low_anchor_values)
                high_anchor = median(high_anchor_values)
                ai = anchoring_index(
                    high_point,
                    low_point,
                    high_anchor,
                    low_anchor,
                )
                if math.isfinite(ai):
                    item_ais.append(ai)
                    if (
                        control_point is not None
                        and low_anchor < control_point < high_anchor
                    ):
                        valid_baseline_ais.append(ai)
                    human_values = _finite(
                        [row.get("human_ai") for row in low_rows + high_rows]
                    )
                    if human_values:
                        correlated_item_ais.append(ai)
                        human_ais.append(median(human_values))

            if control_width is not None:
                for condition_rows in (low_rows, high_rows):
                    anchored_width = _median_field(condition_rows, "value")
                    if anchored_width is not None:
                        width_deltas.append(width_delta(anchored_width, control_width))

            if control_point is not None:
                for condition_rows in (low_rows, high_rows):
                    for row in condition_rows:
                        anchor = row.get("anchor")
                        raw_answer = str(row.get("comparative_answer") or "").lower()
                        answer_match = re.search(r"\b(greater|less)\b", raw_answer)
                        if anchor is None or answer_match is None:
                            continue
                        answer = answer_match.group(1)
                        expected = "greater" if control_point > float(anchor) else "less"
                        all_comparisons += 1
                        consistent_comparisons += answer == expected

        provenance_summaries[provenance] = {
            "items_with_complete_pairs": len(item_ais),
            "items_with_valid_baseline": len(valid_baseline_ais),
            "items_with_nonzero_effect": sum(abs(value) > 1e-12 for value in item_ais),
            "median_anchoring_index": median(item_ais) if item_ais else None,
            "mean_anchoring_index": (
                sum(item_ais) / len(item_ais) if item_ais else None
            ),
            "mean_absolute_anchoring_index": (
                sum(abs(value) for value in item_ais) / len(item_ais)
                if item_ais
                else None
            ),
            "valid_baseline_median_anchoring_index": (
                median(valid_baseline_ais) if valid_baseline_ais else None
            ),
            "valid_baseline_mean_anchoring_index": (
                sum(valid_baseline_ais) / len(valid_baseline_ais)
                if valid_baseline_ais
                else None
            ),
            "human_ai_spearman": _spearman(correlated_item_ais, human_ais),
            "median_width_delta": median(width_deltas) if width_deltas else None,
        }

    return {
        "parse_rate": parse_rate,
        "comparative_consistency": (
            consistent_comparisons / all_comparisons if all_comparisons else None
        ),
        "comparisons_scored": all_comparisons,
        "by_provenance": provenance_summaries,
    }


def _format(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def print_summary(run: dict[str, Any], summary: dict[str, Any]) -> None:
    print(f"Model: {run['model']}")
    print(f"Log: {run['log']}")
    print(f"Samples: {run['samples']}")
    print(f"Parse rate: {_format(summary['parse_rate'])}")
    print(
        "Comparative consistency: "
        f"{_format(summary['comparative_consistency'])} "
        f"(n={summary['comparisons_scored']})"
    )
    for provenance, values in summary["by_provenance"].items():
        print(f"\n{provenance.upper()} provenance")
        print(f"  Complete item pairs: {values['items_with_complete_pairs']}")
        print(f"  Valid-baseline items: {values['items_with_valid_baseline']}")
        print(f"  Nonzero item effects: {values['items_with_nonzero_effect']}")
        print(f"  Median anchoring index: {_format(values['median_anchoring_index'])}")
        print(f"  Mean anchoring index: {_format(values['mean_anchoring_index'])}")
        print(
            "  Mean absolute anchoring index: "
            f"{_format(values['mean_absolute_anchoring_index'])}"
        )
        print(
            "  Valid-baseline mean AI: "
            f"{_format(values['valid_baseline_mean_anchoring_index'])}"
        )
        print(f"  Human-AI Spearman: {_format(values['human_ai_spearman'])}")
        print(f"  Median width delta: {_format(values['median_width_delta'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", nargs="?", help="Inspect .eval log; defaults to newest J&K log")
    parser.add_argument("--output", type=Path, help="optional JSON summary destination")
    args = parser.parse_args()

    path = args.log or _latest_jk_log()
    rows, run = rows_from_log(path)
    summary = summarize(rows)
    print_summary(run, summary)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps({"run": run, "summary": summary}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
