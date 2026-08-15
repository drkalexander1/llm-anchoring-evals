from __future__ import annotations

import pytest
import pandas as pd

from scripts.analyze_jk import summarize
from scripts.build_human_audit import CONDITIONS, MODEL_PAIRS, MODELS
from scripts.import_r3 import build_baselines
from scripts.power_analysis import _required_n
from src.anchoring_metrics import anchoring_index, beta_high, beta_low
from src.anchors import (
    derive_anchors,
    derive_matched_distance_anchors,
    derive_outside_anchors,
    interp_quantile,
)
from src.consistency import (
    classify_same_turn_consistency,
    parse_comparative_direction,
)
from src.inspect_util import load_prompt
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


def test_strong_anchors_extend_beyond_stated_interval() -> None:
    assert derive_outside_anchors(220, 240, 260, strength=2) == (200, 280)
    with pytest.raises(ValueError, match="positive finite"):
        derive_outside_anchors(220, 240, 260, strength=0)


def test_matched_distance_anchors_are_symmetric_around_p50() -> None:
    low, high = derive_matched_distance_anchors(200, 240, 300, strength=2)
    assert high - 240 == pytest.approx(240 - low)
    # Outside anchors are asymmetric (160 vs 360); matched uses mean distance.
    assert derive_outside_anchors(200, 240, 300, strength=2) == (160, 360)
    assert (low, high) == (140, 340)


def test_comparative_direction_parser_accepts_true_labels() -> None:
    assert parse_comparative_direction("TRUE_GREATER") == "greater"
    assert parse_comparative_direction("true_less") == "less"
    assert parse_comparative_direction("Greater.") == "greater"
    assert parse_comparative_direction("nope") is None


def test_same_turn_consistency_flags_whole_interval_contradictions() -> None:
    assert (
        classify_same_turn_consistency("greater", 100, 10, 20, 30)
        == "whole_interval_contradicted"
    )
    assert (
        classify_same_turn_consistency("TRUE_LESS", 10, 20, 30, 40)
        == "whole_interval_contradicted"
    )
    assert classify_same_turn_consistency("greater", 10, 20, 30, 40) == "consistent"
    assert (
        classify_same_turn_consistency("less", 50, 10, 60, 90) == "p50_inconsistent"
    )


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


def test_r7_taxon_subset_uses_matched_control_and_strong_anchors() -> None:
    dataset = anchored_dataset(
        "taxon",
        "taxonomy-r3/claude-haiku-4-5@2026-07-02",
        1,
        anchor_method="outside",
        anchor_strength=2,
        matched_control=True,
        subset_path="data/taxon_subset_r7.yaml",
    )

    assert len(dataset) == 90
    controls = [sample for sample in dataset if sample.metadata["condition"] == "control"]
    anchored = [sample for sample in dataset if sample.metadata["anchor"] is not None]
    assert len(controls) == 18
    assert all(sample.metadata["matched_control"] for sample in controls)
    assert all(sample.metadata["estimate_prompt"] for sample in controls)
    assert all(sample.metadata["anchor_method"] == "outside" for sample in anchored)


def test_r8_true_labels_and_matched_distance_scaffold() -> None:
    arm_a = anchored_dataset(
        "taxon",
        "taxonomy-r3/claude-haiku-4-5@2026-07-02",
        1,
        anchor_method="outside",
        anchor_strength=2,
        matched_control=True,
        subset_path="data/contradiction_subset_r8.yaml",
        comparative_labels="true_greater_less",
    )
    arm_b = anchored_dataset(
        "taxon",
        "taxonomy-r3/claude-haiku-4-5@2026-07-02",
        1,
        anchor_method="matched_distance",
        anchor_strength=2,
        matched_control=True,
        subset_path="data/contradiction_subset_r8.yaml",
        comparative_labels="greater_less",
    )

    assert len(arm_a) == 40
    assert len(arm_b) == 40
    assert all(
        sample.metadata["comparative_labels"] == "true_greater_less" for sample in arm_a
    )
    assert all(
        sample.metadata["anchor_method"] == "matched_distance"
        for sample in arm_b
        if sample.metadata["anchor"] is not None
    )

    high_a = next(s for s in arm_a if s.metadata["condition"] == "high_arb")
    high_b = next(
        s
        for s in arm_b
        if s.metadata["item_id"] == high_a.metadata["item_id"]
        and s.metadata["condition"] == "high_arb"
    )
    assert "TRUE_GREATER" in str(high_a.input)
    assert "TRUE_LESS" in str(high_a.input)
    assert "greater" in str(high_b.input).lower()
    assert "TRUE_GREATER" not in str(high_b.input)

    true_arb = load_prompt("anchor_compare_arb_true.txt")
    true_plaus = load_prompt("anchor_compare_plaus_true.txt")
    assert "TRUE_GREATER" in true_arb and "TRUE_LESS" in true_arb
    assert "TRUE_GREATER" in true_plaus and "TRUE_LESS" in true_plaus


def test_r10_jk_true_labels() -> None:
    dataset = anchored_dataset(
        "jk",
        None,
        1,
        comparative_labels="true_greater_less",
    )
    assert len(dataset) == 75
    anchored = [sample for sample in dataset if sample.metadata["anchor"] is not None]
    assert len(anchored) == 60
    assert all(
        sample.metadata["comparative_labels"] == "true_greater_less"
        for sample in dataset
    )
    assert all("TRUE_GREATER" in str(sample.input) for sample in anchored)
    assert all("TRUE_LESS" in str(sample.input) for sample in anchored)


def test_dataset_rejects_unknown_comparative_labels() -> None:
    with pytest.raises(ValueError, match="comparative_labels"):
        anchored_dataset(
            "taxon",
            "taxonomy-r3/claude-haiku-4-5@2026-07-02",
            1,
            comparative_labels="not_a_label",
        )


def test_r9_sham_factorial_uses_forced_true_tokens() -> None:
    dataset = anchored_dataset(
        "taxon",
        "taxonomy-r3/claude-haiku-4-5@2026-07-02",
        1,
        anchor_method="outside",
        anchor_strength=2,
        subset_path="data/contradiction_subset_r8.yaml",
        first_turn_mode="sham",
    )

    # 8 items × 3 first-turns × 2 provenances × 2 directions
    assert len(dataset) == 96
    assert all(sample.metadata["condition"] != "control" for sample in dataset)
    first_turns = {sample.metadata["first_turn"] for sample in dataset}
    assert first_turns == {"ready", "forced_true_greater", "forced_true_less"}

    forced = next(
        s for s in dataset if s.metadata["first_turn"] == "forced_true_greater"
    )
    ready = next(s for s in dataset if s.metadata["first_turn"] == "ready")
    assert "TRUE_GREATER" in str(forced.input)
    assert "ready" in str(ready.input).lower()
    assert "TRUE_GREATER" not in str(ready.input)


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
        assert values["items_with_valid_baseline"] == 1
        assert values["items_with_nonzero_effect"] == 1
        assert values["median_anchoring_index"] == pytest.approx(0.5)
        assert values["mean_anchoring_index"] == pytest.approx(0.5)
        assert values["mean_absolute_anchoring_index"] == pytest.approx(0.5)
        assert values["valid_baseline_mean_anchoring_index"] == pytest.approx(0.5)
        assert values["median_width_delta"] == pytest.approx(-0.2)
        assert values["human_ai_spearman"] is None


def test_analysis_keeps_taxon_effects_without_human_ai() -> None:
    rows = [
        {
            "item_id": "taxon",
            "condition": "control",
            "parsed": True,
            "point": 50,
            "value": 0.4,
        },
        {
            "item_id": "taxon",
            "condition": "low_arb",
            "parsed": True,
            "point": 25,
            "value": 0.3,
            "anchor": 0,
        },
        {
            "item_id": "taxon",
            "condition": "high_arb",
            "parsed": True,
            "point": 75,
            "value": 0.3,
            "anchor": 100,
        },
    ]

    result = summarize(rows)["by_provenance"]["arb"]

    assert result["items_with_complete_pairs"] == 1
    assert result["items_with_valid_baseline"] == 1
    assert result["mean_anchoring_index"] == pytest.approx(0.5)
    assert result["human_ai_spearman"] is None


def test_r3_baseline_import_prefers_later_duplicate() -> None:
    first = pd.DataFrame(
        [{"model": "model", "prompt_key": "item", "p10": 1, "p50": 2, "p90": 3}]
    )
    second = pd.DataFrame(
        [{"model": "model", "prompt_key": "item", "p10": 4, "p50": 5, "p90": 6}]
    )

    result = build_baselines(
        [
            (first, "first.csv", "2026-07-01"),
            (second, "second.csv", "2026-07-02"),
        ]
    )

    assert len(result) == 1
    assert result.iloc[0]["point"] == 5


def test_power_calculation_scales_with_effect_retention() -> None:
    assert _required_n(0.5, 0.8, 1.0) == 25
    assert _required_n(0.5, 0.8, 0.5) == 99
    assert _required_n(-0.1, 0.8, 1.0) is None


def test_human_audit_schedule_is_balanced() -> None:
    model_counts = {model: 0 for model in MODELS}
    for pairs in MODEL_PAIRS.values():
        assert len(pairs) == len(CONDITIONS)
        for pair in pairs:
            assert len(set(pair)) == 2
            for model_index in pair:
                model_counts[MODELS[model_index]] += 1

    assert set(model_counts.values()) == {5}
