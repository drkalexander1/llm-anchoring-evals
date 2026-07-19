"""Pilot-based power analysis for sizing the harder taxon arm.

The experimental unit is an item. Effect sizes come from the completed J&K
bridge runs and are evaluated at several retention levels because taxon anchors
are milder. Required sample sizes use a one-sided normal approximation for a
one-sample mean test at alpha=.05.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Any

from inspect_ai.log import list_eval_logs, read_eval_log

from src.anchoring_metrics import anchoring_index

MODELS = (
    "anthropic/claude-sonnet-4-5-20250929",
    "anthropic/claude-haiku-4-5-20251001",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
)
PROVENANCES = ("arb", "plaus")
Z_ALPHA_ONE_SIDED = 1.644854
Z_POWER = {0.8: 0.841621, 0.9: 1.281552}
RETENTION = (1.0, 0.75, 0.5, 0.25)


def _latest_complete_logs(log_dir: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for info in list_eval_logs(log_dir, descending=True):
        header = read_eval_log(info, header_only=True)
        if (
            header.status != "success"
            or header.eval.task != "elicit_anchored"
            or header.eval.metadata.get("item_set") != "jk"
            or header.eval.model not in MODELS
            or header.eval.dataset.samples != 75
            or header.eval.model in found
        ):
            continue
        found[header.eval.model] = info.name
    missing = set(MODELS) - set(found)
    if missing:
        raise FileNotFoundError(f"missing complete J&K logs for {sorted(missing)}")
    return found


def _item_ais(path: str) -> dict[str, dict[str, float]]:
    log = read_eval_log(path)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for sample in log.samples or []:
        score = (sample.scores or {}).get("anchored_ci_scorer")
        if score is None or not score.value:
            continue
        metadata = score.metadata or {}
        grouped[(str(metadata["item_id"]), str(metadata["condition"]))].append(metadata)

    output: dict[str, dict[str, float]] = defaultdict(dict)
    item_ids = {key[0] for key in grouped}
    for item_id in item_ids:
        for provenance in PROVENANCES:
            low = grouped[(item_id, f"low_{provenance}")]
            high = grouped[(item_id, f"high_{provenance}")]
            if not low or not high:
                continue
            value = anchoring_index(
                float(high[0]["point"]),
                float(low[0]["point"]),
                float(high[0]["anchor"]),
                float(low[0]["anchor"]),
            )
            if math.isfinite(value):
                output[item_id][provenance] = value
    return dict(output)


def _required_n(effect_size: float, power: float, retention: float) -> int | None:
    adjusted = effect_size * retention
    if adjusted <= 0:
        return None
    return math.ceil(((Z_ALPHA_ONE_SIDED + Z_POWER[power]) / adjusted) ** 2)


def _effect_summary(values: list[float]) -> dict[str, Any]:
    mu = mean(values)
    sigma = stdev(values)
    effect_size = mu / sigma if sigma > 0 else None
    sensitivity: dict[str, Any] = {}
    for retention in RETENTION:
        sensitivity[f"{int(retention * 100)}pct"] = {
            f"power_{int(power * 100)}": (
                _required_n(effect_size, power, retention)
                if effect_size is not None
                else None
            )
            for power in Z_POWER
        }
    return {
        "pilot_items": len(values),
        "mean": mu,
        "sd": sigma,
        "standardized_effect": effect_size,
        "required_items": sensitivity,
    }


def analyze(log_dir: str) -> dict[str, Any]:
    logs = _latest_complete_logs(log_dir)
    by_model = {model: _item_ais(path) for model, path in logs.items()}
    effects: dict[str, Any] = {}

    for model, items in by_model.items():
        for provenance in PROVENANCES:
            values = [
                item[provenance] for item in items.values() if provenance in item
            ]
            effects[f"{model}:{provenance}"] = _effect_summary(values)
        deltas = [
            item["plaus"] - item["arb"]
            for item in items.values()
            if set(PROVENANCES) <= set(item)
        ]
        effects[f"{model}:provenance_delta"] = _effect_summary(deltas)

    common_items = set.intersection(*(set(items) for items in by_model.values()))
    pooled: dict[str, list[float]] = {key: [] for key in (*PROVENANCES, "provenance_delta")}
    for item_id in sorted(common_items):
        for provenance in PROVENANCES:
            pooled[provenance].append(
                mean(by_model[model][item_id][provenance] for model in MODELS)
            )
        pooled["provenance_delta"].append(
            mean(
                by_model[model][item_id]["plaus"]
                - by_model[model][item_id]["arb"]
                for model in MODELS
            )
        )
    for name, values in pooled.items():
        effects[f"all_models:{name}"] = _effect_summary(values)

    return {
        "method": {
            "test": "one-sided one-sample mean, normal approximation",
            "alpha": 0.05,
            "powers": list(Z_POWER),
            "effect_retention": list(RETENTION),
            "experimental_unit": "item",
            "taxon_calls_per_item_across_four_models": 36,
            "note": "Pilot estimates use 15 J&K items; taxon transfer is uncertain.",
        },
        "logs": logs,
        "effects": effects,
    }


def _display_n(value: int | None) -> str:
    if value is None:
        return "n/a"
    return ">54" if value > 54 else str(value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument(
        "--output", type=Path, default=Path("results/power_analysis.json")
    )
    args = parser.parse_args()

    result = analyze(args.log_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("Pooled across the four fixed models")
    for endpoint in ("arb", "plaus", "provenance_delta"):
        summary = result["effects"][f"all_models:{endpoint}"]
        full = summary["required_items"]["100pct"]["power_80"]
        half = summary["required_items"]["50pct"]["power_80"]
        print(
            f"  {endpoint}: mean={summary['mean']:.3f}, "
            f"d={summary['standardized_effect']:.3f}, "
            f"n80={_display_n(full)}, n80@50%={_display_n(half)}"
        )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
