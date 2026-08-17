"""Compare R10 J&K TRUE_* contradiction rates to Round 6 ambiguous labels."""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

from scripts.analyze_contradiction import annotate_rows, is_whole_interval_contradiction
from scripts.analyze_jk import rows_from_log

R6_AMBIGUOUS = {
    "anthropic/claude-haiku-4-5-20251001": (9, 60),
    "anthropic/claude-sonnet-4-5-20250929": (7, 60),
}


def _discover(eval_name: str, n_samples: int, labels: str) -> dict[str, str]:
    selected: dict[str, str] = {}
    for info in list_eval_logs("logs", descending=True):
        log = read_eval_log(info, header_only=True)
        if log.status != "success" or log.eval.task != "elicit_anchored":
            continue
        meta = log.eval.metadata or {}
        if meta.get("item_set") != "jk":
            continue
        if meta.get("comparative_labels", "greater_less") != labels:
            continue
        if eval_name and meta.get("eval") != eval_name:
            continue
        full = read_eval_log(info)
        if len(full.samples or []) != n_samples:
            continue
        model = log.eval.model
        if model not in selected:
            selected[model] = info.name
    return selected


def _rate(path: str) -> dict:
    rows, run = rows_from_log(path)
    rows = annotate_rows(rows)
    anchored = [
        r for r in rows if r.get("condition") != "control" and r.get("parsed")
    ]
    n = len(anchored)
    c = sum(
        1
        for r in anchored
        if is_whole_interval_contradiction(r["same_turn_consistency"])
    )
    high = [r for r in anchored if r.get("direction") == "high"]
    low = [r for r in anchored if r.get("direction") == "low"]
    ch = sum(
        1
        for r in high
        if is_whole_interval_contradiction(r["same_turn_consistency"])
    )
    cl = sum(
        1
        for r in low
        if is_whole_interval_contradiction(r["same_turn_consistency"])
    )
    return {
        "run": run,
        "anchored_comparisons": n,
        "whole_interval_contradicted": c,
        "by_direction": {
            "high": {"n": len(high), "whole_interval_contradicted": ch},
            "low": {"n": len(low), "whole_interval_contradicted": cl},
        },
    }


def main() -> None:
    r10 = _discover("anchoring-r10", 75, "true_greater_less")
    out = {"models": []}
    print(f"{'model':28} R6 ambiguous     R10 TRUE_*")
    for model in sorted(R6_AMBIGUOUS):
        if model not in r10:
            print(f"{model.split('/')[-1]:28} MISSING R10 LOG")
            continue
        stats = _rate(r10[model])
        log_name = Path(str(stats["run"]["log"]).replace("file://", "")).name
        stats["run"]["log"] = f"logs/{log_name}"
        c6, n6 = R6_AMBIGUOUS[model]
        c10 = stats["whole_interval_contradicted"]
        n10 = stats["anchored_comparisons"]
        stats["r6_ambiguous"] = {"whole_interval_contradicted": c6, "n": n6}
        out["models"].append({"model": model, **stats})
        short = model.split("/")[-1]
        print(
            f"{short:28} {c6}/{n6} ({c6/n6:.0%})     "
            f"{c10}/{n10} ({c10/n10:.0%})  "
            f"high {stats['by_direction']['high']['whole_interval_contradicted']}/"
            f"{stats['by_direction']['high']['n']}"
        )
    Path("results/r10_jk_true_contradiction.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote results/r10_jk_true_contradiction.json")


if __name__ == "__main__":
    main()
