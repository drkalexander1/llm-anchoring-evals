"""Import the R3 bird-taxonomy item bank and B0 intervals for the taxon arm.

Example:
    python scripts/import_r3.py \
      --r3-root C:/Users/chaos/Projects/bird-taxonomy-evals \
      --baseline results/latest_inspect/by_prompt.csv=2026-07-02

Additional baseline CSVs can be supplied by repeating ``--baseline``. Later
files replace duplicate (model, item) rows from earlier files.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

REQUIRED_COLUMNS = {
    "prompt_key",
    "model",
    "taxonomic_level",
    "genus",
    "family",
    "order",
    "ioc_count",
    "p10",
    "p50",
    "p90",
}


def _parse_source(spec: str, r3_root: Path) -> tuple[Path, str]:
    try:
        path_text, run_date = spec.rsplit("=", 1)
    except ValueError as exc:
        raise ValueError(
            f"baseline must use PATH=YYYY-MM-DD syntax, got {spec!r}"
        ) from exc
    path = Path(path_text)
    if not path.is_absolute():
        path = r3_root / path
    if not path.is_file():
        raise FileNotFoundError(path)
    return path, run_date


def _read_source(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")
    if frame[list(REQUIRED_COLUMNS)].isnull().any().any():
        raise ValueError(f"{path} contains null values in required columns")
    return frame


def _question(row: Any) -> str:
    level = str(row.taxonomic_level)
    if level not in {"genus", "family", "order"}:
        raise ValueError(f"unexpected taxonomic_level {level!r}")
    taxon = str(getattr(row, level))
    return (
        f"How many bird species are currently recognized in the "
        f"{level} {taxon} worldwide?"
    )


def build_items(frame: pd.DataFrame) -> list[dict[str, Any]]:
    unique = frame.sort_values("prompt_key").drop_duplicates("prompt_key")
    items = [
        {
            "id": str(row.prompt_key),
            "question": _question(row),
            "answer_scale": "linear",
            "true_value": float(row.ioc_count),
            "unit": "species",
            "notes": f"R3 taxon arm; level={row.taxonomic_level}",
        }
        for row in unique.itertuples(index=False)
    ]
    if len(items) != 54:
        raise ValueError(f"expected 54 current taxon items, found {len(items)}")
    return items


def build_baselines(sources: list[tuple[pd.DataFrame, Path, str]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for frame, path, run_date in sources:
        for row in frame.itertuples(index=False):
            rows.append(
                {
                    "model_snapshot": f"taxonomy-r3/{row.model}@{run_date}",
                    "item_id": str(row.prompt_key),
                    "lower": float(row.p10),
                    "point": float(row.p50),
                    "upper": float(row.p90),
                    "source": str(path),
                }
            )
    output = pd.DataFrame(rows)
    output["_model"] = output["model_snapshot"].str.replace(
        r"^taxonomy-r3/|@\d{4}-\d{2}-\d{2}$", "", regex=True
    )
    output = output.drop_duplicates(["_model", "item_id"], keep="last")
    output = output.drop(columns="_model").sort_values(["model_snapshot", "item_id"])
    return output.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r3-root", type=Path, required=True)
    parser.add_argument(
        "--baseline",
        action="append",
        help="R3 by_prompt.csv and run date as PATH=YYYY-MM-DD; repeatable",
    )
    parser.add_argument("--items-out", type=Path, default=Path("data/items.yaml"))
    parser.add_argument("--baselines-out", type=Path, default=Path("data/prior_b.csv"))
    args = parser.parse_args()

    specs = args.baseline or [
        "results/latest_inspect/by_prompt.csv=2026-07-02"
    ]
    loaded: list[tuple[pd.DataFrame, Path, str]] = []
    for spec in specs:
        path, run_date = _parse_source(spec, args.r3_root)
        loaded.append((_read_source(path), path, run_date))

    items = build_items(loaded[0][0])
    baselines = build_baselines(loaded)

    args.items_out.parent.mkdir(parents=True, exist_ok=True)
    args.baselines_out.parent.mkdir(parents=True, exist_ok=True)
    args.items_out.write_text(
        yaml.safe_dump({"items": items}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    baselines.to_csv(args.baselines_out, index=False)

    counts = baselines.groupby("model_snapshot").size()
    print(f"Wrote {len(items)} items to {args.items_out}")
    print(f"Wrote {len(baselines)} baseline rows to {args.baselines_out}")
    for model, count in counts.items():
        print(f"  {model}: {count}")


if __name__ == "__main__":
    main()
