"""Score Round 6 AI on the frozen timeless vs time-sensitive J&K split."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median

import yaml
from inspect_ai.log import list_eval_logs, read_eval_log

from scripts.analyze_jk import rows_from_log, summarize

CODEBOOK = Path("data/jk_temporal_split.yaml")


def _discover_r6() -> dict[str, str]:
    selected: dict[str, str] = {}
    for info in list_eval_logs("logs", descending=True):
        log = read_eval_log(info, header_only=True)
        if log.status != "success" or log.eval.task != "elicit_anchored":
            continue
        meta = log.eval.metadata or {}
        if meta.get("item_set") != "jk":
            continue
        if meta.get("comparative_labels", "greater_less") != "greater_less":
            continue
        if meta.get("eval") == "anchoring-r10":
            continue
        full = read_eval_log(info)
        if len(full.samples or []) != 75:
            continue
        model = log.eval.model
        if model not in selected:
            selected[model] = info.name
    return selected


def _human_mean(item_ids: list[str], items: list[dict]) -> float:
    by_id = {row["id"]: float(row["human_ai"]) for row in items}
    return mean(by_id[i] for i in item_ids)


def _slice_summary(rows: list[dict], item_ids: set[str]) -> dict:
    sliced = [r for r in rows if r.get("item_id") in item_ids]
    summary = summarize(sliced)
    compact = {}
    for prov, vals in summary["by_provenance"].items():
        compact[prov] = {
            "n_pairs": vals["items_with_complete_pairs"],
            "n_nonzero": vals["items_with_nonzero_effect"],
            "mean_ai": vals["mean_anchoring_index"],
            "median_ai": vals["median_anchoring_index"],
            "valid_baseline_n": vals["items_with_valid_baseline"],
            "valid_baseline_mean_ai": vals["valid_baseline_mean_anchoring_index"],
        }
    return compact


def main() -> None:
    book = yaml.safe_load(CODEBOOK.read_text(encoding="utf-8"))
    items = yaml.safe_load(Path("data/jk_items.yaml").read_text(encoding="utf-8"))["items"]
    timeless = list(book["timeless"])
    aging = list(book["time_sensitive"])
    # yaml may attach comments via strings like "jk_cat_speed  # biology..."
    timeless = [t.split()[0] for t in timeless]
    aging = [t.split()[0] for t in aging]

    out = {
        "codebook": str(CODEBOOK),
        "timeless_ids": timeless,
        "time_sensitive_ids": aging,
        "human_mean_ai_timeless": _human_mean(timeless, items),
        "human_mean_ai_time_sensitive": _human_mean(aging, items),
        "models": [],
    }
    print(
        f"human mean AI  timeless={out['human_mean_ai_timeless']:.3f}  "
        f"aging={out['human_mean_ai_time_sensitive']:.3f}"
    )
    for model, path in sorted(_discover_r6().items()):
        rows, run = rows_from_log(path)
        rec = {
            "model": model,
            "log": "logs/" + Path(str(run["log"]).replace("file://", "")).name,
            "timeless": _slice_summary(rows, set(timeless)),
            "time_sensitive": _slice_summary(rows, set(aging)),
        }
        out["models"].append(rec)
        short = model.split("/")[-1]
        for label, block in (("timeless", rec["timeless"]), ("aging", rec["time_sensitive"])):
            arb = block["arb"]
            plaus = block["plaus"]
            print(
                f"{short:28} {label:16} "
                f"arb mean={arb['mean_ai']:+.3f} med={arb['median_ai']:+.3f} "
                f"plaus mean={plaus['mean_ai']:+.3f} med={plaus['median_ai']:+.3f} "
                f"nonzero {arb['n_nonzero']}/{arb['n_pairs']} | {plaus['n_nonzero']}/{plaus['n_pairs']}"
            )
    Path("results/r10_jk_temporal_split.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote results/r10_jk_temporal_split.json")


if __name__ == "__main__":
    main()
