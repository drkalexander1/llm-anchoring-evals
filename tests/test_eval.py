from __future__ import annotations

import pytest

from scripts.analyze_jk import summarize
from src.anchoring_metrics import anchoring_index, beta_high, beta_low
from src.anchors import derive_anchors, interp_quantile
from src.schema import parse_ci_triple
from src.tasks.elicit_anchored import anchored_dataset


def test_jk_mississippi_index_reproduces_published_value() -> None:
    value = anchoring_index(1500, 300, 2000, 70)
    assert value == pytest.approx(0.62, abs=0.005)


def test_anchor_interpolation_and_pull_metrics() -> None:
    assert interp_quantile(220, 240, 260, 0.15) == pytest.approx(222.5)
    assert interp_quantile(220, 240, 260, 0.85) == pytest.approx(257.5)
    assert derive_anchors(220, 240, 260) == (222, 258)
    assert beta_low(50, 25, 0) == pytest.approx(0.5)
    assert beta_high(50, 75, 100) == pytest.approx(0.5)


def test_ci_parser_requires_ordered_triple() -> None:
    assert parse_ci_triple("10 20 30") == (10.0, 20.0, 30.0)
    assert parse_ci_triple("30 20 10") is None
    assert parse_ci_triple("not an interval") is None


def test_jk_dataset_has_expected_factorial_structure() -> None:
    dataset = anchored_dataset("jk", None, 1)
    assert len(dataset) == 75
    conditions = [sample.metadata["condition"] for sample in dataset]
    assert conditions.count("control") == 15
    assert conditions.count("low_arb") == 15
    assert conditions.count("high_arb") == 15
    assert conditions.count("low_plaus") == 15
    assert conditions.count("high_plaus") == 15


def test_dataset_rejects_nonpositive_repeat_count() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        anchored_dataset("jk", None, 0)


def test_analysis_summary_computes_effects_and_consistency() -> None:
    rows = [
        {
            "item_id": "item",
            "condition": "control",
            "parsed": True,
            "point": 50,
            "value": 0.4,
        }
    ]
    for provenance in ("arb", "plaus"):
        rows.extend(
            [
                {
                    "item_id": "item",
                    "condition": f"low_{provenance}",
                    "parsed": True,
                    "point": 25,
                    "value": 0.2,
                    "anchor": 0,
                    "human_ai": 0.5,
                    "comparative_answer": "Greater.",
                },
                {
                    "item_id": "item",
                    "condition": f"high_{provenance}",
                    "parsed": True,
                    "point": 75,
                    "value": 0.2,
                    "anchor": 100,
                    "human_ai": 0.5,
                    "comparative_answer": "less",
                },
            ]
        )

    result = summarize(rows)

    assert result["parse_rate"] == 1
    assert result["comparative_consistency"] == 1
    assert result["comparisons_scored"] == 4
    for provenance in ("arb", "plaus"):
        values = result["by_provenance"][provenance]
        assert values["items_with_nonzero_effect"] == 1
        assert values["median_anchoring_index"] == pytest.approx(0.5)
        assert values["mean_anchoring_index"] == pytest.approx(0.5)
        assert values["mean_absolute_anchoring_index"] == pytest.approx(0.5)
        assert values["median_width_delta"] == pytest.approx(-0.2)
        assert values["human_ai_spearman"] is None
