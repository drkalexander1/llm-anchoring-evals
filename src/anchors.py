"""Anchor placement for R6.

Two arms place anchors differently -- ON PURPOSE:

* jk_bridge arm: anchors are the ORIGINAL human-calibrated values from
  jk_items.yaml (J&K Table 1). Do not derive them; identical stimulus is the
  point of the human comparison. Just read low_anchor/high_anchor.

* taxon arm: anchors are placed at the 15th/85th percentiles of the *model's
  own* estimate distribution -- the single-subject analog of J&K's method,
  where anchors sit at the 15th/85th percentiles of the calibration GROUP's
  estimates (paper p.1161-1162).

=========================  DESIGN DECISION (resolve first)  ==================
J&K's calibration distribution is the spread of point estimates ACROSS PEOPLE.
For one model there are two analogs, and they give different anchors:

  (A) VERBALIZED  -- interpolate the 15th/85th percentiles from the model's own
      stated CI (p10/p50/p90 = B0). Cheap, no extra sampling. Implemented here
      as the default. Caveat: the model's stated CI is its *verbalized*
      uncertainty, not an empirical estimate spread, so p15/p85 sit just inside
      [p10, p90] and the resulting anchors are relatively MILD.

  (B) RESAMPLED   -- sample the model's point answer N times at temperature and
      take the 15/85 percentiles of that empirical distribution. Truer to J&K's
      construction, but N x more calls; this is the R5 "signal D" object.

Pick one deliberately and say which in the write-up. To use (B), build an
empirical quantile function per (model,item) and call `percentile_anchor` with
it instead of the stated-CI interpolation. Everything downstream is identical.
=============================================================================
"""

from __future__ import annotations

import math
from typing import Callable

from src.schema import AnswerScale

# CDF knots implied by an 80% central interval: p10/p50/p90 sit at these
# cumulative probabilities.
_KNOTS = (0.10, 0.50, 0.90)


def interp_quantile(
    lower: float,
    point: float,
    upper: float,
    q: float,
    scale: AnswerScale = "linear",
) -> float:
    """Value at cumulative probability `q` by piecewise-linear interpolation of
    the stated CI knots (0.10->lower, 0.50->point, 0.90->upper).

    For log-scale items the interpolation is done in log10 space. `q` outside
    [0.10, 0.90] is linearly extrapolated on the nearest segment (fine for the
    15th/85th percentiles, which are interior).
    """
    x0, x1, x2 = _KNOTS
    if scale == "log":
        if min(lower, point, upper) <= 0:
            raise ValueError("log-scale anchors require positive bounds")
        y0, y1, y2 = math.log10(lower), math.log10(point), math.log10(upper)
    else:
        y0, y1, y2 = lower, point, upper

    if q <= x1:  # lower segment [0.10, 0.50] (covers q = 0.15)
        val = y0 + (y1 - y0) * (q - x0) / (x1 - x0)
    else:        # upper segment [0.50, 0.90] (covers q = 0.85)
        val = y1 + (y2 - y1) * (q - x1) / (x2 - x1)

    return 10.0**val if scale == "log" else val


def _round_anchor(value: float, scale: AnswerScale) -> float:
    """Present anchors as clean numbers so they don't leak precision cues.

    Rounds to ~2 significant figures. Adjust if an item needs finer anchors.
    """
    if value == 0 or not math.isfinite(value):
        return value
    digits = 1 - int(math.floor(math.log10(abs(value))))
    return round(value, max(digits, 0)) if abs(value) >= 1 else round(value, 2)


def derive_anchors(
    lower: float,
    point: float,
    upper: float,
    scale: AnswerScale = "linear",
    low_q: float = 0.15,
    high_q: float = 0.85,
    round_values: bool = True,
) -> tuple[float, float]:
    """(low_anchor, high_anchor) for the taxon arm, analog (A) above."""
    low = interp_quantile(lower, point, upper, low_q, scale)
    high = interp_quantile(lower, point, upper, high_q, scale)
    if round_values:
        low, high = _round_anchor(low, scale), _round_anchor(high, scale)
    return low, high


def derive_outside_anchors(
    lower: float,
    point: float,
    upper: float,
    scale: AnswerScale = "linear",
    strength: float = 2.0,
    round_values: bool = True,
) -> tuple[float, float]:
    """Place anchors outside B0 by a multiple of each side's uncertainty.

    ``strength=1`` reproduces p10/p90. ``strength=2`` places each anchor twice
    as far from p50 as the corresponding stated interval bound. This is the R7
    taxon default and is deliberately stronger than the R6 p15/p85 analog.
    """
    if strength <= 0 or not math.isfinite(strength):
        raise ValueError("anchor strength must be a positive finite number")
    if not lower <= point <= upper:
        raise ValueError("anchor derivation requires lower <= point <= upper")

    if scale == "log":
        if lower <= 0:
            raise ValueError("log-scale anchors require positive bounds")
        lo, mid, hi = math.log10(lower), math.log10(point), math.log10(upper)
        low = 10.0 ** (mid - strength * (mid - lo))
        high = 10.0 ** (mid + strength * (hi - mid))
    else:
        low = point - strength * (point - lower)
        high = point + strength * (upper - point)

    if round_values:
        low, high = _round_anchor(low, scale), _round_anchor(high, scale)
    return low, high


def percentile_anchor(
    quantile_fn: Callable[[float], float],
    low_q: float = 0.15,
    high_q: float = 0.85,
    scale: AnswerScale = "linear",
    round_values: bool = True,
) -> tuple[float, float]:
    """Analog (B): pass an empirical quantile function (e.g. from resampled
    point answers) and get the 15th/85th-percentile anchors from it."""
    low, high = quantile_fn(low_q), quantile_fn(high_q)
    if round_values:
        low, high = _round_anchor(low, scale), _round_anchor(high, scale)
    return low, high
