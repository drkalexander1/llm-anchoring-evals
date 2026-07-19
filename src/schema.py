"""Item bank, record schema, and parsing helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from src import DEFAULT_ITEMS_PATH

AnswerScale = Literal["linear", "log"]
Signal = Literal["A", "B", "C", "D"]


class Item(BaseModel):
    id: str
    question: str
    answer_scale: AnswerScale = "linear"
    true_value: float | None = None
    unit: str | None = None
    notes: str | None = None


class SignalRecord(BaseModel):
    """Long-form per-item record for offline analysis (design schema)."""

    model_snapshot: str
    item_id: str
    run_id: str
    signal: Signal
    value: float
    elicitation_order_seed: int | None = None
    timestamp: str | None = None
    raw: str | None = None
    excluded: bool = False
    exclusion_reason: str | None = None
    metadata: dict = Field(default_factory=dict)


def load_items(path: Path | None = None) -> list[Item]:
    path = path or DEFAULT_ITEMS_PATH
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Item.model_validate(row) for row in payload["items"]]


def format_item_list(items: list[Item]) -> str:
    return "\n".join(f"{item.id}: {item.question}" for item in items)


_NUMBER_RE = re.compile(
    r"""
    [+-]?
    (?:
        (?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?
    )
    """,
    re.VERBOSE,
)

_LABELED_LINE_RE = re.compile(
    r"^\s*([A-Za-z0-9_]+)\s*:\s*([+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?)\s*$"
)


def parse_labeled_widths(
    text: str,
    item_ids: list[str],
) -> list[float | None]:
    """Parse `item_id: number` lines; align to expected item_ids order."""
    found: dict[str, float] = {}
    for line in text.strip().splitlines():
        line = line.strip().strip("`").strip()
        if not line:
            continue
        match = _LABELED_LINE_RE.match(line)
        if match is None:
            # tolerate markdown bullets / bold
            cleaned = re.sub(r"^[-*]\s*", "", line)
            cleaned = cleaned.replace("**", "")
            match = _LABELED_LINE_RE.match(cleaned)
        if match is None:
            continue
        item_id = match.group(1).lower()
        try:
            found[item_id] = float(match.group(2))
        except ValueError:
            continue
    return [found.get(i.lower()) for i in item_ids]


def parse_numeric_column(text: str, expected: int | None = None) -> list[float | None]:
    """Extract one number per non-empty line; None for unparseable lines."""
    values: list[float | None] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = _NUMBER_RE.search(line.replace(",", ""))
        if match is None:
            values.append(None)
            continue
        try:
            values.append(float(match.group(0)))
        except ValueError:
            values.append(None)
    if expected is not None and len(values) != expected:
        # Pad / truncate so callers can zip against item order and log mismatches.
        if len(values) < expected:
            values.extend([None] * (expected - len(values)))
        else:
            values = values[:expected]
    return values


def parse_single_number(text: str) -> float | None:
    match = _NUMBER_RE.search(text.replace(",", ""))
    if match is None:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_ci_triple(text: str) -> tuple[float, float, float] | None:
    nums = [float(m.group(0)) for m in _NUMBER_RE.finditer(text.replace(",", ""))]
    if len(nums) < 3:
        return None
    lower, point, upper = nums[0], nums[1], nums[2]
    if not (lower <= point <= upper):
        return None
    return lower, point, upper


def relative_width(lower: float, point: float, upper: float, scale: AnswerScale) -> float:
    """Normalize CI width so magnitude doesn't dominate correlations."""
    if scale == "log":
        if lower <= 0 or upper <= 0:
            raise ValueError("log-scale width requires positive bounds")
        import math

        return math.log10(upper) - math.log10(lower)
    denom = abs(point) if point != 0 else abs((lower + upper) / 2.0)
    if denom == 0:
        return float("nan")
    return (upper - lower) / denom


def canonical_model_id(model_snapshot: str) -> str:
    """Bare model name for joining R3 B tags with Inspect provider/model ids.

    Examples:
      taxonomy-r3/claude-sonnet-4-6@2026-06-21 -> claude-sonnet-4-6
      anthropic/claude-sonnet-4-6               -> claude-sonnet-4-6
      openai/gpt-4o                            -> gpt-4o
      claude-haiku-4-5                         -> claude-haiku-4-5
    """
    name = model_snapshot.strip()
    if "/" in name:
        name = name.rsplit("/", 1)[-1]
    if "@" in name:
        name = name.split("@", 1)[0]
    return name
