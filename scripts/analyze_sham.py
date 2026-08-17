"""Summarize sham-token (Round 9 / R10 Sonnet 5) logs vs ready."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from inspect_ai.log import list_eval_logs, read_eval_log

from scripts.analyze_contradiction import annotate_rows, is_whole_interval_contradiction
from scripts.analyze_jk import rows_from_log
from src.anchoring_metrics import anchoring_index


def _discover_sham(n_samples: int = 96) -> dict[str, str]:
    selected: dict[str, str] = {}
    for info in list_eval_logs("logs", descending=True):
        log = read_eval_log(info, header_only=True)
        if log.status != "success" or log.eval.task != "elicit_anchored":
            continue
        meta = log.eval.metadata or {}
        if meta.get("first_turn_mode") != "sham":
            continue
        full = read_eval_log(info)
        if len(full.samples or []) != n_samples:
            continue
        model = log.eval.model
        if model not in selected:
            selected[model] = info.name
    return selected


def _cell_key(row: dict) -> tuple:
    return (row["item_id"], row["condition"])


def _mean_ai(rows: list[dict], provenance: str) -> float | None:
    by_item: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        if not row.get("parsed") or row.get("provenance") != provenance:
            continue
        by_item[str(row["item_id"])][str(row["direction"])] = float(row["point"])
        by_item[str(row["item_id"])][f"a_{row['direction']}"] = float(row["anchor"])
    ais = []
    for vals in by_item.values():
        if "low" in vals and "high" in vals:
            ai = anchoring_index(vals["high"], vals["low"], vals["a_high"], vals["a_low"])
            if ai is not None:
                ais.append(float(ai))
    return mean(ais) if ais else None


def summarize_sham_log(path: str) -> dict:
    rows, run = rows_from_log(path)
    rows = annotate_rows(rows)
    ready_p50 = {}
    for row in rows:
        if row.get("first_turn") != "ready" or not row.get("parsed"):
            continue
        ready_p50[_cell_key(row)] = float(row["point"])
    by_arm: dict[str, dict] = {}
    grouped: dict[str, list] = defaultdict(list)
    for row in rows:
        if not row.get("parsed"):
            continue
        grouped[str(row.get("first_turn"))].append(row)
    for arm, arm_rows in grouped.items():
        deltas = []
        contrad = 0
        n_forced = 0
        zeros = 0
        for row in arm_rows:
            key = _cell_key(row)
            if key not in ready_p50:
                continue
            d = float(row["point"]) - ready_p50[key]
            deltas.append(d)
            if d == 0.0:
                zeros += 1
            if arm != "ready":
                n_forced += 1
                if is_whole_interval_contradiction(row["same_turn_consistency"]):
                    contrad += 1
        by_arm[arm] = {
            "n": len(arm_rows),
            "mean_p50_minus_ready": mean(deltas) if deltas else None,
            "median_p50_minus_ready": median(deltas) if deltas else None,
            "exact_zero_share": (zeros / len(deltas)) if deltas else None,
            "whole_interval_contradicted": None if arm == "ready" else contrad,
            "mean_ai_arb": _mean_ai(arm_rows, "arb"),
            "mean_ai_plaus": _mean_ai(arm_rows, "plaus"),
        }
    log_name = Path(str(run["log"]).replace("file://", "")).name
    run["log"] = f"logs/{log_name}"
    return {"run": run, "by_first_turn": by_arm}


def main() -> None:
    models = []
    for model, path in sorted(_discover_sham().items()):
        rec = summarize_sham_log(path)
        models.append(rec)
        short = model.split("/")[-1]
        ft = rec["by_first_turn"]
        g = ft.get("forced_true_greater", {})
        less = ft.get("forced_true_less", {})
        print(
            f"{short:28} dG={g.get('mean_p50_minus_ready'):+.2f} "
            f"dL={less.get('mean_p50_minus_ready'):+.2f} "
            f"zeroG={g.get('exact_zero_share'):.0%} zeroL={less.get('exact_zero_share'):.0%} "
            f"cG={g.get('whole_interval_contradicted')} cL={less.get('whole_interval_contradicted')}"
        )
    Path("results/r10_sham_all_models_summary.json").write_text(
        json.dumps({"models": models}, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote results/r10_sham_all_models_summary.json")


if __name__ == "__main__":
    main()
