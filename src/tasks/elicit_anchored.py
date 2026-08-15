"""Anchored-CI elicitation shared by the R6 J&K and R7 taxon arms.

Faithful Tversky-Kahneman two-step: Turn 1 asks a comparative greater/less
judgment against an anchor; Turn 2 elicits the model's own p10/p50/p90 in the
same context. R7 can use a matched two-turn control whose first response is a
neutral `ready` acknowledgement.

Conditions per item: control, low_arb, high_arb, low_plaus, high_plaus.
Anchors:
  * taxon arm  -> stronger out-of-interval anchors derived per-model from B0
  * jk_bridge  -> original human-calibrated anchors from data/jk_items.yaml

Run (taxon arm; anchors come from prior_b for the SAME model):
    See R7_TAXON_PLAN.md for the predeclared model-specific commands.

Run (J&K bridge arm; fixed anchors, model-independent):
    inspect eval src/tasks/elicit_anchored.py \
        --model anthropic/claude-sonnet-4-6 -T item_set=jk
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml
from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ChatMessageUser, GenerateConfig
from inspect_ai.scorer import Score, Scorer, Target, mean, scorer, stderr
from inspect_ai.solver import Generate, TaskState, generate, solver

from src import DATA_DIR, DEFAULT_PRIOR_B_PATH, ROOT
from src.anchors import (
    derive_anchors,
    derive_matched_distance_anchors,
    derive_outside_anchors,
)
from src.inspect_util import load_prompt
from src.schema import canonical_model_id, load_items, parse_ci_triple, relative_width

PROVENANCES = ("arb", "plaus")
DIRECTIONS = ("low", "high")
COMPARATIVE_LABELS = ("greater_less", "true_greater_less")
# Round 9 sham first-turns (anchored cells only; no unanchored control).
SHAM_FIRST_TURNS = ("ready", "forced_true_greater", "forced_true_less")
FIRST_TURN_MODES = ("comparative", "sham")


# --------------------------------------------------------------------------- #
# Dataset
# --------------------------------------------------------------------------- #
def _taxon_anchors(
    baseline_model: str,
    anchor_method: str,
    anchor_strength: float,
) -> dict[str, tuple[float, float, str]]:
    """item_id -> (low_anchor, high_anchor, answer_scale) from a model's B0.

    baseline_model is matched by canonical id, so
    'taxonomy-r3/claude-sonnet-4-6@2026-06-21' and 'anthropic/claude-sonnet-4-6'
    resolve to the same rows.
    """
    scales = {it.id: it.answer_scale for it in load_items()}
    df = pd.read_csv(DEFAULT_PRIOR_B_PATH)
    want = canonical_model_id(baseline_model)
    out: dict[str, tuple[float, float, str]] = {}
    for row in df.itertuples(index=False):
        if canonical_model_id(str(row.model_snapshot)) != want:
            continue
        scale = scales.get(str(row.item_id), "linear")
        if anchor_method == "outside":
            low, high = derive_outside_anchors(
                float(row.lower),
                float(row.point),
                float(row.upper),
                scale,
                strength=anchor_strength,
            )
        elif anchor_method == "matched_distance":
            low, high = derive_matched_distance_anchors(
                float(row.lower),
                float(row.point),
                float(row.upper),
                scale,
                strength=anchor_strength,
            )
        elif anchor_method == "quantile":
            low, high = derive_anchors(
                float(row.lower), float(row.point), float(row.upper), scale
            )
        else:
            raise ValueError(
                "anchor_method must be 'outside', 'matched_distance', or "
                f"'quantile', got {anchor_method!r}"
            )
        out[str(row.item_id)] = (low, high, scale)
    if not out:
        raise ValueError(
            f"no prior_b rows matched baseline_model={baseline_model!r} "
            f"(canonical {want!r}); pass -T baseline_model=<snapshot in prior_b.csv>"
        )
    return out


def _load_jk() -> list[dict]:
    payload = yaml.safe_load((DATA_DIR / "jk_items.yaml").read_text(encoding="utf-8"))
    return payload["items"]


def _load_subset(path: str | None) -> set[str] | None:
    if path is None:
        return None
    subset_path = Path(path)
    if not subset_path.is_absolute():
        subset_path = ROOT / subset_path
    payload = yaml.safe_load(subset_path.read_text(encoding="utf-8"))
    item_ids = payload.get("item_ids") if isinstance(payload, dict) else None
    if not isinstance(item_ids, list) or not item_ids:
        raise ValueError(f"{path} must contain a non-empty item_ids list")
    return {str(item_id) for item_id in item_ids}


def _anchor_str(value: float) -> str:
    """Render an anchor without a trailing .0 on integers."""
    return str(int(value)) if float(value).is_integer() else str(value)


def _compare_prompt_name(provenance: str, comparative_labels: str) -> str:
    if comparative_labels == "true_greater_less":
        return f"anchor_compare_{provenance}_true.txt"
    if comparative_labels == "greater_less":
        return f"anchor_compare_{provenance}.txt"
    raise ValueError(
        "comparative_labels must be 'greater_less' or 'true_greater_less', "
        f"got {comparative_labels!r}"
    )


def _first_turn_prompt_name(provenance: str, first_turn: str) -> str:
    if first_turn == "ready":
        return f"anchor_ready_{provenance}.txt"
    if first_turn == "forced_true_greater":
        return f"anchor_force_true_greater_{provenance}.txt"
    if first_turn == "forced_true_less":
        return f"anchor_force_true_less_{provenance}.txt"
    raise ValueError(
        "first_turn must be 'ready', 'forced_true_greater', or "
        f"'forced_true_less', got {first_turn!r}"
    )


def _sample(
    *,
    item_id: str,
    question: str,
    condition: str,
    scale: str,
    seed: int,
    anchor: float | None,
    provenance: str | None,
    direction: str | None,
    matched_control: bool = False,
    comparative_labels: str = "greater_less",
    first_turn: str = "comparative",
    extra: dict | None = None,
) -> Sample:
    base_meta = {
        "item_id": item_id,
        "condition": condition,
        "answer_scale": scale,
        "elicitation_order_seed": seed,
        "anchor": anchor,
        "provenance": provenance,
        "direction": direction,
        "matched_control": matched_control,
        "comparative_labels": comparative_labels,
        "first_turn": first_turn,
        **(extra or {}),
    }
    if condition == "control":
        if matched_control:
            return Sample(
                input=load_prompt("control_ready.txt").format(question=question),
                id=f"{item_id}::control::s{seed}",
                metadata={
                    **base_meta,
                    "estimate_prompt": load_prompt("anchor_estimate.txt"),
                    "matched_control": True,
                },
            )
        # R6-compatible single-turn unanchored CI (signal B baseline).
        return Sample(
            input=load_prompt("ci_b.txt").format(question=question),
            id=f"{item_id}::control::s{seed}",
            metadata={
                **base_meta,
                "estimate_prompt": None,
                "matched_control": False,
            },
        )
    if first_turn in SHAM_FIRST_TURNS:
        tmpl = load_prompt(_first_turn_prompt_name(str(provenance), first_turn))
        return Sample(
            input=tmpl.format(question=question, anchor=_anchor_str(float(anchor))),
            id=f"{item_id}::{condition}::{first_turn}::s{seed}",
            metadata={
                **base_meta,
                "estimate_prompt": load_prompt("anchor_estimate.txt"),
            },
        )
    # anchored: Turn 1 = comparative; Turn 2 prompt carried in metadata
    compare_tmpl = load_prompt(_compare_prompt_name(provenance, comparative_labels))
    return Sample(
        input=compare_tmpl.format(question=question, anchor=_anchor_str(anchor)),
        id=f"{item_id}::{condition}::s{seed}",
        metadata={**base_meta, "estimate_prompt": load_prompt("anchor_estimate.txt")},
    )


def anchored_dataset(
    item_set: str,
    baseline_model: str | None,
    seeds: int,
    *,
    anchor_method: str = "outside",
    anchor_strength: float = 2.0,
    matched_control: bool = False,
    subset_path: str | None = None,
    comparative_labels: str = "greater_less",
    first_turn_mode: str = "comparative",
) -> MemoryDataset:
    if seeds < 1:
        raise ValueError(f"seeds must be at least 1, got {seeds}")
    if comparative_labels not in COMPARATIVE_LABELS:
        raise ValueError(
            "comparative_labels must be 'greater_less' or 'true_greater_less', "
            f"got {comparative_labels!r}"
        )
    if first_turn_mode not in FIRST_TURN_MODES:
        raise ValueError(
            "first_turn_mode must be 'comparative' or 'sham', "
            f"got {first_turn_mode!r}"
        )
    if first_turn_mode == "sham" and item_set != "taxon":
        raise ValueError("first_turn_mode='sham' is only supported for item_set=taxon")

    samples: list[Sample] = []

    if item_set == "taxon":
        if not baseline_model:
            raise ValueError("taxon arm requires -T baseline_model=<snapshot in prior_b.csv>")
        anchors = _taxon_anchors(baseline_model, anchor_method, anchor_strength)
        subset = _load_subset(subset_path)
        available_items = {it.id: it for it in load_items() if it.id in anchors}
        if subset is not None:
            missing = subset - set(available_items)
            if missing:
                raise ValueError(f"subset contains unknown item ids: {sorted(missing)}")
            items = {
                item_id: item
                for item_id, item in available_items.items()
                if item_id in subset
            }
        else:
            items = available_items
        first_turns = (
            SHAM_FIRST_TURNS if first_turn_mode == "sham" else ("comparative",)
        )
        for seed in range(seeds):
            for item_id, item in items.items():
                low, high, scale = anchors[item_id]
                shared = {
                    "baseline_model": canonical_model_id(baseline_model),
                    "anchor_method": anchor_method,
                    "anchor_strength": anchor_strength,
                    "subset_path": subset_path,
                    "comparative_labels": comparative_labels,
                    "first_turn_mode": first_turn_mode,
                }
                if first_turn_mode == "comparative":
                    samples.append(_sample(
                        item_id=item_id, question=item.question,
                        condition="control", scale=scale, seed=seed,
                        anchor=None, provenance=None, direction=None,
                        matched_control=matched_control,
                        comparative_labels=comparative_labels,
                        first_turn="comparative",
                        extra=shared,
                    ))
                for first_turn in first_turns:
                    for prov in PROVENANCES:
                        for dirn, aval in (("low", low), ("high", high)):
                            samples.append(_sample(
                                item_id=item_id, question=item.question,
                                condition=f"{dirn}_{prov}", scale=scale, seed=seed,
                                anchor=aval, provenance=prov, direction=dirn,
                                matched_control=matched_control,
                                comparative_labels=comparative_labels,
                                first_turn=first_turn,
                                extra=shared,
                            ))

    elif item_set == "jk":
        for seed in range(seeds):
            for row in _load_jk():
                scale = row.get("answer_scale", "linear")
                samples.append(_sample(item_id=row["id"], question=row["question"],
                                       condition="control", scale=scale, seed=seed,
                                       anchor=None, provenance=None, direction=None,
                                       comparative_labels=comparative_labels,
                                       extra={"human_ai": row.get("human_ai")}))
                for prov in PROVENANCES:
                    for dirn in DIRECTIONS:
                        samples.append(_sample(
                            item_id=row["id"], question=row["question"],
                            condition=f"{dirn}_{prov}", scale=scale, seed=seed,
                            anchor=float(row[f"{dirn}_anchor"]), provenance=prov, direction=dirn,
                            comparative_labels=comparative_labels,
                            extra={"human_ai": row.get("human_ai"),
                                   "calibration_median": row.get("calibration_median")},
                        ))
    else:
        raise ValueError(f"item_set must be 'taxon' or 'jk', got {item_set!r}")

    return MemoryDataset(samples, name=f"elicit_anchored_{item_set}")


# --------------------------------------------------------------------------- #
# Solver: two-turn for anchors and optionally for the matched control
# --------------------------------------------------------------------------- #
@solver
def anchored_two_turn():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        # Turn 1 is already the sample input; generate acknowledgement / token.
        state = await generate(state)
        first_turn = state.metadata.get("first_turn", "comparative")
        if state.metadata.get("condition") == "control":
            if not state.metadata.get("estimate_prompt"):
                return state  # R6 single-turn control.
            state.metadata["control_acknowledgement"] = state.output.completion.strip()
        elif first_turn in SHAM_FIRST_TURNS:
            state.metadata["sham_answer"] = state.output.completion.strip()
            # Keep comparative_answer populated for forced TRUE_* arms so
            # existing consistency helpers can score them.
            state.metadata["comparative_answer"] = state.output.completion.strip()
        else:
            state.metadata["comparative_answer"] = state.output.completion.strip()
        # Turn 2: elicit the model's own CI in the same context.
        state.messages.append(ChatMessageUser(content=state.metadata["estimate_prompt"]))
        state = await generate(state)
        return state

    return solve


# --------------------------------------------------------------------------- #
# Scorer: parse the final CI triple; carry all anchoring metadata to export
# --------------------------------------------------------------------------- #
@scorer(metrics=[mean(), stderr()])
def anchored_ci_scorer() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        m = state.metadata
        triple = parse_ci_triple(state.output.completion)
        carried = {
            "signal": "B_anchored",
            "item_id": m["item_id"],
            "condition": m["condition"],
            "anchor": m.get("anchor"),
            "provenance": m.get("provenance"),
            "direction": m.get("direction"),
            "elicitation_order_seed": m.get("elicitation_order_seed"),
            "comparative_answer": m.get("comparative_answer"),
            "answer_scale": m["answer_scale"],
            "baseline_model": m.get("baseline_model"),
            "human_ai": m.get("human_ai"),
            "matched_control": m.get("matched_control", False),
            "control_acknowledgement": m.get("control_acknowledgement"),
            "anchor_method": m.get("anchor_method"),
            "anchor_strength": m.get("anchor_strength"),
            "subset_path": m.get("subset_path"),
            "comparative_labels": m.get("comparative_labels", "greater_less"),
            "first_turn": m.get("first_turn", "comparative"),
            "first_turn_mode": m.get("first_turn_mode", "comparative"),
            "sham_answer": m.get("sham_answer"),
        }
        if triple is None:
            return Score(value=0.0, answer=state.output.completion,
                         explanation="failed to parse p10/p50/p90",
                         metadata={**carried, "point": None, "value": None})
        lower, point, upper = triple
        width = relative_width(lower, point, upper, m["answer_scale"])
        return Score(
            value=1.0, answer=state.output.completion,
            explanation=f"p50={point:g} rel_width={width:.6g}",
            metadata={**carried, "lower": lower, "point": point, "upper": upper,
                      "value": width},  # value=width; point kept for beta
        )

    return score


@task
def elicit_anchored(
    item_set: str = "taxon",
    baseline_model: str | None = None,
    seeds: int = 1,
    temperature: float | None = None,
    anchor_method: str = "outside",
    anchor_strength: float = 2.0,
    matched_control: bool = False,
    subset_path: str | None = None,
    comparative_labels: str = "greater_less",
    first_turn_mode: str = "comparative",
) -> Task:
    """Build the anchoring task.

    ``seeds`` is retained as a pairing/repeat label for compatibility with the
    surrounding eval suite. It does not seed provider-side generation. Keep it
    at 1 for the deterministic portfolio run.

    ``comparative_labels`` selects the first-turn response contract:
    ``greater_less`` (R6/R7) or ``true_greater_less`` (R8 Arm A).

    ``first_turn_mode='sham'`` builds Round 9 ready / forced-TRUE_* arms
    (anchored cells only).
    """
    eval_name = "anchoring-r6"
    if item_set == "jk" and comparative_labels == "true_greater_less":
        eval_name = "anchoring-r10"
    elif item_set == "taxon":
        if first_turn_mode == "sham":
            eval_name = "anchoring-r9"
        elif (
            comparative_labels == "true_greater_less"
            or anchor_method == "matched_distance"
        ):
            eval_name = "anchoring-r8"
        else:
            eval_name = "anchoring-r7"
    return Task(
        dataset=anchored_dataset(
            item_set,
            baseline_model,
            seeds,
            anchor_method=anchor_method,
            anchor_strength=anchor_strength,
            matched_control=matched_control,
            subset_path=subset_path,
            comparative_labels=comparative_labels,
            first_turn_mode=first_turn_mode,
        ),
        solver=anchored_two_turn(),
        scorer=anchored_ci_scorer(),
        config=GenerateConfig(temperature=temperature),
        metadata={
            "eval": eval_name,
            "item_set": item_set,
            "anchor_method": anchor_method if item_set == "taxon" else None,
            "anchor_strength": anchor_strength if item_set == "taxon" else None,
            "matched_control": matched_control,
            "subset_path": subset_path,
            "comparative_labels": comparative_labels,
            "first_turn_mode": first_turn_mode,
        },
    )
