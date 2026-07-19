"""R6 anchoring metrics. Pure functions over the joined per-item table.

All formulas verified against Jacowitz & Kahneman 1995 (PSPB 21(11):1161-1166):

  Two-anchor AI (their headline, p.1162):
      AI = [median(high) - median(low)] / [high_anchor - low_anchor]

  Per-anchor AI referenced to the baseline (their eq., p.1162):
      AI(low)  = [median(low)  - median(cal)] / [low_anchor  - median(cal)]
      AI(high) = [median(high) - median(cal)] / [high_anchor - median(cal)]

  For an LLM, `median(cal)` is replaced by the SAME model's unanchored baseline
  p50 (B0) -- a within-subject counterfactual J&K's between-group design could
  not run. beta_low/beta_high below are exactly AI(low)/AI(high) with that
  substitution; they are J&K's index, not a new construct.

  beta = 0 immune | 1 snapped to anchor | (0,1) partial | <0 contrast | >1 overshoot.

Edge case: if B0 falls outside [low_anchor, high_anchor] (possible on the JK
bridge arm, where anchors are human-calibrated), a directional denominator can
change sign -> beta uninterpretable. Callers should flag/exclude, not average.
"""

from __future__ import annotations

import numpy as np

_RNG = np.random.default_rng(20260718)


# ----- per-anchor pull (J&K AI(low)/AI(high) with within-subject baseline) --- #
def beta_low(p50_base: float, p50_low: float, low_anchor: float) -> float:
    denom = p50_base - low_anchor
    return float("nan") if denom == 0 else (p50_base - p50_low) / denom


def beta_high(p50_base: float, p50_high: float, high_anchor: float) -> float:
    denom = high_anchor - p50_base
    return float("nan") if denom == 0 else (p50_high - p50_base) / denom


def baseline_in_range(p50_base: float, low_anchor: float, high_anchor: float) -> bool:
    """False => beta denominators may be sign-flipped; flag before averaging."""
    return low_anchor < p50_base < high_anchor


# ----- pooled two-anchor AI (baseline-free; for the human comparison) -------- #
def anchoring_index(p50_high: float, p50_low: float, high_anchor: float, low_anchor: float) -> float:
    denom = high_anchor - low_anchor
    return float("nan") if denom == 0 else (p50_high - p50_low) / denom


# ----- width contamination (RQ1 headline) ----------------------------------- #
def width_delta(width_anchored: float, width_base: float) -> float:
    """Signed change in normalized interval width vs. unanchored control.
    Negative => the anchor NARROWED the interval (false-confidence signal)."""
    return width_anchored - width_base


# ----- aggregation helpers -------------------------------------------------- #
def bootstrap_ci(
    values: np.ndarray,
    stat=np.nanmedian,
    n_boot: int = 10_000,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """(point, lo, hi) percentile bootstrap over items. NaNs ignored by `stat`."""
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    if values.size == 0:
        return (float("nan"),) * 3
    point = float(stat(values))
    idx = _RNG.integers(0, values.size, size=(n_boot, values.size))
    boot = stat(values[idx], axis=1)
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def asymmetry(beta_high_vals: np.ndarray, beta_low_vals: np.ndarray) -> tuple[float, float, float]:
    """High-minus-low pull, bootstrapped. J&K human baseline: .51 vs .40 (p.1163)."""
    return bootstrap_ci(np.asarray(beta_high_vals) - np.asarray(beta_low_vals))


def noise_floor_ok(width_delta_val: float, floor: float) -> bool:
    """Interpret a width shift only if it exceeds the control-seed width jitter."""
    return abs(width_delta_val) > abs(floor)
