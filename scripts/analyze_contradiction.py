"""Reanalyze R7 taxon logs for same-turn contradictions and AI decomposition.

Usage:
    python scripts/analyze_contradiction.py
    python scripts/analyze_contradiction.py --output results/r7_contradiction_decomposition.json
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from inspect_ai.log import list_eval_logs, read_eval_log

from scripts.analyze_jk import rows_from_log
from src.anchoring_metrics import anchoring_index
from src.consistency import (
    classify_same_turn_consistency,
    is_p50_consistent,
    is_whole_interval_contradiction,
    parse_comparative_direction,
)

PROVENANCES = ("arb", "plaus")
R7_SAMPLE_COUNT = 90


def _discover_r7_logs(log_dir: str = "logs") -> list[str]:
    selected: dict[str, str] = {}
    for info in list_eval_logs(log_dir, descending=True):
        log = read_eval_log(info, header_only=True)
        if log.status != "success" or log.eval.task != "elicit_anchored":
            continue
        meta = log.eval.metadata or {}
        if meta.get("item_set") != "taxon":
            continue
        if meta.get("comparative_labels", "greater_less") != "greater_less":
            continue
        if not meta.get("matched_control"):
            continue
        n_samples = getattr(log.eval, "dataset", None)
        # Prefer full 90-sample runs by reading sample count from header when present.
        full = read_eval_log(info)
        if len(full.samples or []) != R7_SAMPLE_COUNT:
            continue
        model = log.eval.model
        if model not in selected:
            selected[model] = info.name
    if len(selected) < 1:
        raise FileNotFoundError(f"no full R7 taxon logs found under {log_dir!r}")
    return list(selected.values())


def annotate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if row.get("condition") == "control":
            kind = "control"
        elif not row.get("parsed"):
            kind = "unparsed"
        else:
            kind = classify_same_turn_consistency(
                row.get("comparative_answer"),
                row.get("anchor"),
                row.get("lower"),
                row.get("point"),
                row.get("upper"),
            )
        out.append(
            {
                **row,
                "comparative_direction": parse_comparative_direction(
                    row.get("comparative_answer")
                ),
                "same_turn_consistency": kind,
            }
        )
    return out


def _item_ai(
    rows: list[dict[str, Any]],
    item_id: str,
    provenance: str,
    *,
    require_consistent: bool,
) -> float | None:
    low = [
        r
        for r in rows
        if r.get("item_id") == item_id
        and r.get("condition") == f"low_{provenance}"
        and r.get("parsed")
    ]
    high = [
        r
        for r in rows
        if r.get("item_id") == item_id
        and r.get("condition") == f"high_{provenance}"
        and r.get("parsed")
    ]
    if require_consistent:
        low = [r for r in low if is_p50_consistent(r["same_turn_consistency"])]
        high = [r for r in high if is_p50_consistent(r["same_turn_consistency"])]
    if not low or not high:
        return None
    ai = anchoring_index(
        median([float(r["point"]) for r in high]),
        median([float(r["point"]) for r in low]),
        median([float(r["anchor"]) for r in high]),
        median([float(r["anchor"]) for r in low]),
    )
    return ai if math.isfinite(ai) else None


def summarize_model(rows: list[dict[str, Any]], run: dict[str, Any]) -> dict[str, Any]:
    anchored = [r for r in rows if r.get("condition") != "control" and r.get("parsed")]
    by_direction: dict[str, dict[str, int]] = defaultdict(
        lambda: {"n": 0, "p50_consistent": 0, "whole_interval_contradicted": 0}
    )
    for row in anchored:
        direction = str(row.get("direction") or "unknown")
        stats = by_direction[direction]
        stats["n"] += 1
        kind = row["same_turn_consistency"]
        if is_p50_consistent(kind):
            stats["p50_consistent"] += 1
        if is_whole_interval_contradiction(kind):
            stats["whole_interval_contradicted"] += 1

    provenance_summaries: dict[str, Any] = {}
    item_ids = sorted({str(r["item_id"]) for r in rows})
    for provenance in PROVENANCES:
        full_ais: list[float] = []
        consistent_ais: list[float] = []
        for item_id in item_ids:
            full = _item_ai(rows, item_id, provenance, require_consistent=False)
            cons = _item_ai(rows, item_id, provenance, require_consistent=True)
            if full is not None:
                full_ais.append(full)
            if cons is not None:
                consistent_ais.append(cons)
        provenance_summaries[provenance] = {
            "full_item_n": len(full_ais),
            "full_mean_ai": (
                sum(full_ais) / len(full_ais) if full_ais else None
            ),
            "full_median_ai": median(full_ais) if full_ais else None,
            "consistent_pair_n": len(consistent_ais),
            "consistent_mean_ai": (
                sum(consistent_ais) / len(consistent_ais) if consistent_ais else None
            ),
            "consistent_median_ai": (
                median(consistent_ais) if consistent_ais else None
            ),
            "mean_ai_drop_when_restricted_to_consistent": (
                (sum(full_ais) / len(full_ais))
                - (sum(consistent_ais) / len(consistent_ais))
                if full_ais and consistent_ais
                else None
            ),
        }

    return {
        "run": run,
        "anchored_comparisons": len(anchored),
        "p50_consistent": sum(
            1 for r in anchored if is_p50_consistent(r["same_turn_consistency"])
        ),
        "whole_interval_contradicted": sum(
            1
            for r in anchored
            if is_whole_interval_contradiction(r["same_turn_consistency"])
        ),
        "by_direction": dict(by_direction),
        "by_provenance": provenance_summaries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="*", help="Inspect .eval logs; defaults to R7 taxon")
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paths = args.logs or _discover_r7_logs(args.log_dir)
    models: list[dict[str, Any]] = []
    for path in paths:
        rows, run = rows_from_log(path)
        annotated = annotate_rows(rows)
        summary = summarize_model(annotated, run)
        models.append(summary)
        print(f"Model: {run['model']}")
        print(f"  Anchored comparisons: {summary['anchored_comparisons']}")
        print(
            "  P50 consistent: "
            f"{summary['p50_consistent']} "
            f"({summary['p50_consistent'] / max(summary['anchored_comparisons'], 1):.3f})"
        )
        print(
            "  Whole-interval contradictions: "
            f"{summary['whole_interval_contradicted']} "
            f"({summary['whole_interval_contradicted'] / max(summary['anchored_comparisons'], 1):.3f})"
        )
        for direction, stats in summary["by_direction"].items():
            print(
                f"  {direction}: contradicted "
                f"{stats['whole_interval_contradicted']}/{stats['n']} "
                f"({stats['whole_interval_contradicted'] / max(stats['n'], 1):.3f})"
            )
        for provenance, values in summary["by_provenance"].items():
            print(
                f"  {provenance}: full mean AI={values['full_mean_ai']!s}, "
                f"consistent-only mean AI={values['consistent_mean_ai']!s}, "
                f"drop={values['mean_ai_drop_when_restricted_to_consistent']!s}"
            )
        print()

    payload = {"models": models}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
