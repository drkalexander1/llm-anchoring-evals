# R6 anchoring eval — code handoff (for Cursor)

> **Future-scope notes:** This file describes the larger taxon integration.
> For the portfolio-ready J&K evaluation, setup, run, analysis, and limitations,
> see `README.md`.

Written to drop into a clone of **eval-meta-consistency** (R5), whose conventions
these files match exactly (Inspect tasks, pydantic schema, `prompts/*.txt` via
`load_prompt`, `temp_for` policy, long-form record export).

## What's here (written + tested)
```
prompts/anchor_compare_arb.txt     Turn 1, arbitrary-provenance anchor
prompts/anchor_compare_plaus.txt   Turn 1, plausible-source anchor
prompts/anchor_estimate.txt        Turn 2, elicit p10/p50/p90
data/jk_items.yaml                 J&K 1995 Table 1: 15 items, exact anchors, human AI (verified vs paper)
src/anchors.py                     taxon-arm anchor derivation from B0 (+ the A/B design decision)
src/tasks/elicit_anchored.py       the two-turn anchored-CI task + dataset builder (CORE)
src/anchoring_metrics.py           beta (=J&K per-anchor AI), two-anchor AI, width-delta, bootstraps
```
(`src/__init__.py`, `src/schema.py`, `src/inspect_util.py`, `prompts/ci_b.txt` are copied
from the template unchanged, so this folder imports and tests on its own.)

## Assemble
1. `git clone https://github.com/drkalexander1/eval-meta-consistency eval-anchoring && cd eval-anchoring`
2. Copy the files above into the matching paths (overwrite nothing except by intent).
3. Populate the taxon item bank + baseline B0 from R3:
   `python scripts/import_r3.py --r3-root ../bird-taxonomy-evals`
   (NOTE: the local `../bird-taxonomy-evals` checkout is currently EMPTY — clone it first:
    `git clone https://github.com/drkalexander1/bird-taxonomy-evals`.)
4. Copy `career-ops-main/data/eval-anchoring-design.md` in as `DESIGN.md`.

## The ONE decision to make before running (see header of src/anchors.py)
Taxon-arm anchors are placed at the 15th/85th percentiles of the model's own
estimate distribution. Two analogs of J&K's calibration-group method:
- **(A) verbalized** — interpolate p15/p85 from the model's stated CI (implemented, default).
- **(B) resampled** — percentiles of N resampled point answers (truer to J&K, N× cost).

**Empirical caveat found while testing (A):** the R3 stated CIs are narrow
(e.g. p10/p50/p90 = 220/240/260 → anchors 222/258), so verbalized anchors land
*just inside* the interval and are **mild** — the taxon arm may show weak point
anchoring. Options: accept it and report it; use more extreme percentiles
(e.g. 5th/95th) via `derive_anchors(low_q=…, high_q=…)`; or switch to analog (B).
The J&K bridge arm is unaffected (fixed human anchors). Your call — don't let it default silently.

## Remaining pieces (mechanical — all record fields already emitted by the scorer)
1. **export_anchoring.py** — add a `signal == "B_anchored"` branch to the template's
   `src/export.py` (or a sibling). Every field is already carried in the scorer metadata:
   `item_id, condition, anchor, provenance, direction, elicitation_order_seed,
    comparative_answer, lower/point/upper, value(=rel_width), baseline_model, human_ai`.
   Emit one row per sample; join control↔anchored on (item_id, seed, model).
2. **analyze_anchoring.py** — using `src/anchoring_metrics.py`:
   - RQ1 width: per (direction×provenance) median `width_delta`, bootstrap CI, gate on
     control-seed width jitter (`noise_floor_ok`).
   - RQ2 β: `beta_low/beta_high` per item (flag rows where `baseline_in_range` is False),
     mean + `asymmetry`.
   - RQ2b/RQ5: two-anchor `anchoring_index` on jk arm; Spearman ρ vs `human_ai` column.
   - RQ3: β and width_delta, arb vs plaus difference, bootstrap.
   - RQ4: Spearman ρ(control width B0, anchoring magnitude) across items.
3. **tests/** — mirror `tests/test_schema.py`; add a J&K-reproduction test
   (anchoring_index(1500,300,2000,70) == 0.62) and an interp_quantile bracket test.

## Run
```bash
# taxon arm (anchors from THIS model's B0 in prior_b.csv):
inspect eval src/tasks/elicit_anchored.py --model anthropic/claude-sonnet-4-6 \
    -T item_set=taxon -T baseline_model=taxonomy-r3/claude-sonnet-4-6@2026-06-21 -T seeds=2
# J&K bridge arm (fixed human anchors, model-independent):
inspect eval src/tasks/elicit_anchored.py --model anthropic/claude-sonnet-4-6 \
    -T item_set=jk -T seeds=2
```

## Validation already done
`py_compile` on all modules; functional test passes: interp_quantile brackets p50
(linear + log), J&K Mississippi AI reproduces .62, β∈(0,1) partial / 1 snapped / 0 immune.
