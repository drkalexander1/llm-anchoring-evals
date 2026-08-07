# R9 sham-token follow-up

## Goal

Separate **token priming** from **reconsideration** after Round 8's label test.

Round 8 showed that clearer `TRUE_GREATER` / `TRUE_LESS` labels collapse
same-turn contradictions for some models (notably Sonnet 4.5) but not others
(Haiku 4.5, GPT-4o; Sonnet 5 partial). What Round 8 cannot tell is whether a
first-turn directional token (`greater` / `less`) itself pulls the second-turn
interval, even when the token is not a sincere comparative judgment.

## Scientific question

Holding the numeric anchor and second-turn estimate prompt fixed, does forcing
the model to emit `greater` vs `less` vs a direction-neutral acknowledgement
change the subsequent p50 / interval?

## Predeclared decision tree

Freeze before looking at results:

1. **Forced-`greater` and forced-`less` pull p50 in opposite directions relative
   to `ready`, with little change in whole-interval contradiction rate**
   - Interpretation: token priming / commitment to the uttered token
   - Headline: part of measured “anchoring” in two-step protocols can be
     self-generated language, not only the numeric anchor

2. **Forced arms match `ready` on location; contradictions persist where they
   did under Round 8 Arm A**
   - Interpretation: residual incoherence is not mainly token priming
   - Headline: same-turn belief inconsistency survives after removing both
     label ambiguity and forced directional tokens

3. **Mixed / model-heterogeneous**
   - Interpretation: report per-model; do not pool a single mechanism claim
   - Headline: same as Round 8 — mechanism depends on the model

Secondary readout (not the fork classifier): change in anchoring index when
comparing low vs high anchors under each sham first-turn, versus the Round 8
ambiguous / `TRUE_*` arms on the same items.

## Arms (all two-turn, matched length)

Reuse `data/contradiction_subset_r8.yaml` (8 items), outside anchors
`strength=2`, matched conversation length.

| Arm | First turn | Purpose |
|---|---|---|
| **ready** | Neutral acknowledgement (existing `control_ready.txt` pattern, but with the same anchored estimate second turn as treatments) | Direction-neutral baseline |
| **forced_greater** | Instruct model to reply with exactly `greater` (or `TRUE_GREATER` — lock below) before estimating | Token-prime high side |
| **forced_less** | Instruct model to reply with exactly `less` (or `TRUE_LESS`) | Token-prime low side |

Provenance: keep both `arb` and `plaus` for continuity with Round 7/8, or drop
to one provenance to cut cost (lock before run). Default recommendation:
**keep both** on the cheap first pair; drop only if budget forces it.

Directions: still run **low and high** anchors so AI remains computable and so
forced-token × anchor-side interactions are visible.

### Prompt contract (to implement)

Forced arms should:

- present the same anchor + question as Round 8 comparative prompts;
- require a single forced token (no sincere greater/less judgment);
- then use the same `anchor_estimate.txt` second turn.

`ready` should:

- not ask for a comparative judgment;
- still be two-turn with the same estimate prompt;
- ideally mention that a number was shown (or match control_ready closely) so
  turn count and “something happened first” are matched — exact wording is an
  implementation detail to freeze in `prompts/` before paid runs.

## Models (staged, honor Round 8 prereg style)

### Stage 1 — first paid run (lock)

Models that still contradicted under Round 8 Arm A:

- `anthropic/claude-haiku-4-5-20251001`
- `openai/gpt-4o`

(GPT-4o mini was already low; Haiku is the clearer persist case. Prefer GPT-4o
over mini for Stage 1 because its Arm A rate stayed high.)

### Stage 2 — only after Stage 1 classifies the fork

- `openai/gpt-4o-mini` (cheap confirm / low-base contrast)
- `anthropic/claude-sonnet-5` (partial Arm A case)
- Optionally Sonnet 4.5 / Opus 4.5 as negative controls (expect little forced-
  token effect if contradictions were mostly label artifacts / already near
  zero)

Do **not** expand Stage 2 until Stage 1 results are written against the
decision tree.

## Primary endpoints

1. **Signed p50 shift:** for each item × provenance × direction, compare
   forced-greater / forced-less p50 to ready p50 (and to the Round 8 Arm A p50
   when available).
2. **Anchoring index:** low vs high under ready / forced-greater / forced-less.
3. **Whole-interval contradiction rate** only where a directional first-turn
   token exists (forced arms); for `ready`, report N/A or a separate
   “interval vs anchor side” descriptive rate without pretending a comparative
   commitment existed.

## Cost sketch

Per model, if 8 items × 2 provenances × 2 directions × 3 sham first-turns × 2
turns:

- **8 × 2 × 2 × 3 = 96 samples → 192 generations / model**

Stage 1 (Haiku + GPT-4o): **~384 generations**.

If provenance is dropped to one (`plaus` only): **~192 generations** for Stage 1.

Smoke: `--limit 3` on one model before the paid Stage 1 batch.

## Implementation checklist (when coding week starts)

1. Branch `r9-sham-token` from `main`.
2. Add prompts: `anchor_force_greater_*.txt`, `anchor_force_less_*.txt`, and a
   ready-with-anchor variant if needed.
3. Extend `elicit_anchored.py` with a first-turn mode
   (`comparative` / `ready` / `forced_greater` / `forced_less`) or a thin
   sibling task that reuses anchors/subset wiring.
4. Analysis script: p50 deltas vs ready; AI by sham arm; optional contradiction
   rates for forced arms.
5. Tests for dataset factorial structure and prompt selection.
6. Mock smoke, then live `--limit 3`, then Stage 1.

## Locked for Stage 1

1. **Forced token spelling:** `TRUE_GREATER` / `TRUE_LESS`
2. **Stage 1 model pair:** Haiku 4.5 + GPT-4o
3. **Provenances:** both `arb` and `plaus`
4. **Anchored shams only** (no extra unanchored ready arm)
5. **Task flag:** `-T first_turn_mode=sham` on `elicit_anchored.py`

## Definition of done

- Decision tree unchanged after seeing Stage 1
- Stage 1 logs + machine-readable summary
- Short write-up section stating which fork applied
- No Stage 2 until that write-up exists
- Tag `r9-sham-token-v1` when Stage 1 (or Stage 1+2) is frozen

## Timing note

This plan is frozen for when coding/API time opens. Prefer shipping Stage 1
cleanly mid/late week over rushing an incomplete Monday drop.
