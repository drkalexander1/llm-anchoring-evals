"""Select the high-count R8 contradiction subset from the R7 taxon pilot.

Keeps items whose known truth count is at least ``--min-truth`` for all listed
models' prior points, preferring the existing R7 strata mix.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from src.schema import canonical_model_id

DEFAULT_MODELS = (
    "claude-haiku-4-5",
    "gpt-4o-mini",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--items", type=Path, default=Path("data/items.yaml"))
    parser.add_argument("--baselines", type=Path, default=Path("data/prior_b.csv"))
    parser.add_argument(
        "--r7-subset", type=Path, default=Path("data/taxon_subset_r7.yaml")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/contradiction_subset_r8.yaml")
    )
    parser.add_argument("--min-truth", type=float, default=20.0)
    parser.add_argument("--min-prior-point", type=float, default=20.0)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    args = parser.parse_args()

    items = {
        str(item["id"]): item
        for item in yaml.safe_load(args.items.read_text(encoding="utf-8"))["items"]
    }
    r7 = yaml.safe_load(args.r7_subset.read_text(encoding="utf-8"))
    baselines = pd.read_csv(args.baselines)
    models = tuple(m.strip() for m in args.models.split(",") if m.strip())

    eligible: list[str] = []
    for item_id in r7["item_ids"]:
        item = items[item_id]
        if float(item["true_value"]) < args.min_truth:
            continue
        ok = True
        for model in models:
            want = canonical_model_id(model)
            frame = baselines[
                (baselines["item_id"] == item_id)
                & (baselines["model_snapshot"].map(canonical_model_id) == want)
            ]
            if frame.empty or float(frame.iloc[0]["point"]) < args.min_prior_point:
                ok = False
                break
        if ok:
            eligible.append(item_id)

    selected = eligible[: args.limit]
    if len(selected) < args.limit:
        raise ValueError(
            f"needed {args.limit} high-count items, found {len(selected)}: {selected}"
        )

    output = {
        "name": "r8_contradiction_pilot",
        "selection": {
            "source_subset": str(args.r7_subset),
            "min_truth": args.min_truth,
            "min_prior_point": args.min_prior_point,
            "models": list(models),
            "eligible_from_r7": eligible,
        },
        "item_ids": selected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(output, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {len(selected)} items to {args.output}")
    for item_id in selected:
        print(f"  {item_id}: truth={items[item_id]['true_value']}")


if __name__ == "__main__":
    main()
