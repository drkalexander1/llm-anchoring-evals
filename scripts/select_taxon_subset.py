"""Select the predeclared stratified R7 taxon pilot subset.

The selection is deterministic, excludes any item with degenerate strong
anchors for a target model, and preserves the source bank's approximate level
mix: 9 genus, 5 family, and 4 order items.
"""

from __future__ import annotations

import argparse
import random
import re
from pathlib import Path

import pandas as pd
import yaml

from src.anchors import derive_outside_anchors
from src.schema import canonical_model_id

DEFAULT_MODELS = (
    "claude-sonnet-4-5-20250929",
    "claude-haiku-4-5",
    "gpt-4o",
    "gpt-4o-mini",
)
TARGET_COUNTS = {
    "genus_well_known": 5,
    "genus_obscure": 4,
    "family": 5,
    "order": 4,
}


def _note_value(notes: str, key: str) -> str | None:
    match = re.search(rf"(?:^|;\s*){re.escape(key)}=([^;]+)", notes)
    return match.group(1).strip() if match else None


def _stratum(item: dict) -> str:
    notes = str(item.get("notes", ""))
    level = _note_value(notes, "level")
    if level == "genus":
        familiarity = _note_value(notes, "familiarity")
        if familiarity not in {"well_known", "obscure"}:
            raise ValueError(f"missing genus familiarity for {item['id']}")
        return f"genus_{familiarity}"
    if level in {"family", "order"}:
        return level
    raise ValueError(f"missing taxonomic level for {item['id']}")


def eligible_item_ids(
    items: list[dict],
    baselines: pd.DataFrame,
    models: tuple[str, ...],
    strength: float,
) -> set[str]:
    eligible = {str(item["id"]) for item in items}
    for model in models:
        want = canonical_model_id(model)
        frame = baselines[
            baselines["model_snapshot"].map(canonical_model_id) == want
        ]
        if frame.empty:
            raise ValueError(f"no baseline rows matched {model!r}")
        valid: set[str] = set()
        for row in frame.itertuples(index=False):
            low, high = derive_outside_anchors(
                float(row.lower),
                float(row.point),
                float(row.upper),
                strength=strength,
            )
            if low < float(row.point) < high:
                valid.add(str(row.item_id))
        eligible &= valid
    return eligible


def select_subset(
    items: list[dict],
    eligible: set[str],
    seed: int,
) -> tuple[list[str], dict[str, list[str]]]:
    rng = random.Random(seed)
    by_stratum: dict[str, list[str]] = {key: [] for key in TARGET_COUNTS}
    for item in items:
        item_id = str(item["id"])
        if item_id in eligible:
            by_stratum[_stratum(item)].append(item_id)

    selected_by_stratum: dict[str, list[str]] = {}
    for stratum, count in TARGET_COUNTS.items():
        candidates = sorted(by_stratum[stratum])
        if len(candidates) < count:
            raise ValueError(
                f"stratum {stratum} needs {count} items, only {len(candidates)} eligible"
            )
        selected_by_stratum[stratum] = sorted(rng.sample(candidates, count))

    selected = sorted(
        item_id
        for item_ids in selected_by_stratum.values()
        for item_id in item_ids
    )
    return selected, selected_by_stratum


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--items", type=Path, default=Path("data/items.yaml"))
    parser.add_argument("--baselines", type=Path, default=Path("data/prior_b.csv"))
    parser.add_argument(
        "--output", type=Path, default=Path("data/taxon_subset_r7.yaml")
    )
    parser.add_argument("--seed", type=int, default=20260720)
    parser.add_argument("--anchor-strength", type=float, default=2.0)
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    args = parser.parse_args()

    payload = yaml.safe_load(args.items.read_text(encoding="utf-8"))
    items = payload["items"]
    baselines = pd.read_csv(args.baselines)
    models = tuple(model.strip() for model in args.models.split(",") if model.strip())
    eligible = eligible_item_ids(items, baselines, models, args.anchor_strength)
    selected, selected_by_stratum = select_subset(items, eligible, args.seed)

    output = {
        "name": "r7_taxon_pilot",
        "selection": {
            "seed": args.seed,
            "anchor_method": "outside",
            "anchor_strength": args.anchor_strength,
            "models": list(models),
            "eligible_items": len(eligible),
            "strata": selected_by_stratum,
        },
        "item_ids": selected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(output, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {len(selected)} items from {len(eligible)} eligible to {args.output}")
    for stratum, item_ids in selected_by_stratum.items():
        print(f"  {stratum}: {len(item_ids)}")


if __name__ == "__main__":
    main()
