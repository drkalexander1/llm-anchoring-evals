"""Same-turn comparative consistency helpers for R7/R8 audits."""

from __future__ import annotations

import re
from typing import Literal

ComparativeDirection = Literal["greater", "less"]
ConsistencyKind = Literal[
    "consistent",
    "p50_inconsistent",
    "whole_interval_contradicted",
    "tie_at_anchor",
    "unparsed",
]


_TRUE_RE = re.compile(r"\btrue[_\s-]*(greater|less)\b", re.IGNORECASE)
_PLAIN_RE = re.compile(r"\b(greater|less)\b", re.IGNORECASE)


def parse_comparative_direction(raw: str | None) -> ComparativeDirection | None:
    """Extract greater/less from plain or TRUE_GREATER / TRUE_LESS answers."""
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    true_match = _TRUE_RE.search(text)
    if true_match is not None:
        return true_match.group(1).lower()  # type: ignore[return-value]
    plain_match = _PLAIN_RE.search(text)
    if plain_match is not None:
        return plain_match.group(1).lower()  # type: ignore[return-value]
    return None


def classify_same_turn_consistency(
    comparative_answer: str | None,
    anchor: float | None,
    lower: float | None,
    point: float | None,
    upper: float | None,
) -> ConsistencyKind:
    """Compare the first-turn judgment with the same-conversation interval."""
    direction = parse_comparative_direction(comparative_answer)
    if (
        direction is None
        or anchor is None
        or lower is None
        or point is None
        or upper is None
    ):
        return "unparsed"

    anchor_f = float(anchor)
    lo, pt, hi = float(lower), float(point), float(upper)

    if direction == "greater" and hi < anchor_f:
        return "whole_interval_contradicted"
    if direction == "less" and lo > anchor_f:
        return "whole_interval_contradicted"
    if pt == anchor_f:
        return "tie_at_anchor"
    if (direction == "greater" and pt > anchor_f) or (
        direction == "less" and pt < anchor_f
    ):
        return "consistent"
    return "p50_inconsistent"


def is_whole_interval_contradiction(kind: ConsistencyKind) -> bool:
    return kind == "whole_interval_contradicted"


def is_p50_consistent(kind: ConsistencyKind) -> bool:
    return kind == "consistent"
