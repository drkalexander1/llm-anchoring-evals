# LLM anchoring evaluations

This Inspect AI evaluation series asks whether an irrelevant number shifts an
LLM's estimate and confidence interval. The preserved `r6-jk-v1` release adapts
the two-step procedure from Jacowitz and Kahneman (1995):

1. Ask whether the answer is greater or less than an anchor.
2. Ask for the model's own p10, p50, and p90 estimate.

The portfolio-ready scope is the **J&K bridge arm**: 15 published questions,
each evaluated with an unanchored control and low/high anchors described as
either arbitrary or plausible. The same numeric anchors were used in the human
study, enabling an exploratory historical comparison. Several quantities have
changed since 1995, so the full-set comparison is accompanied by a
baseline-bracketing sensitivity analysis.

## What this demonstrates

- A multi-turn Inspect AI evaluation with structured metadata and scoring
- A within-model control and a 2 × 2 direction/provenance intervention
- Reproduction of the published anchoring-index calculation
- Honest analysis of effect size, interval-width changes, parse rate, and
  comparative-response consistency

This is a compact portfolio experiment, not a powered behavioral study. The
15-item human comparison is exploratory, and the one-turn control versus
two-turn treatment is a known protocol limitation.

The completed four-model findings are summarized in [`RESULTS.md`](RESULTS.md);
machine-readable summaries are under `results/`.
Taxon-arm sizing and the recommended staged design are documented in
[`POWER_ANALYSIS.md`](POWER_ANALYSIS.md).
For a portfolio-ready narrative covering the motivation, implementation,
findings, failures, and next iteration, see [`WRITEUP.md`](WRITEUP.md).
The active R7 follow-up is specified in [`R7_TAXON_PLAN.md`](R7_TAXON_PLAN.md).

## Setup

Python 3.11+ is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
```

Set the API key required by the provider you plan to use. Do not commit it.

## Run

Each run contains 75 samples and 135 model calls. This first-pass portfolio
comparison deliberately uses lower-cost models to expose design flaws before a
later run on current frontier models. It is a pragmatic tier comparison, not a
release-matched provider benchmark:

```powershell
$env:PYTHONPATH = (Get-Location).Path
inspect eval src/tasks/elicit_anchored.py `
  --model anthropic/claude-sonnet-4-5-20250929 `
  -T item_set=jk `
  -T seeds=1 `
  -T temperature=0

inspect eval src/tasks/elicit_anchored.py `
  --model anthropic/claude-haiku-4-5-20251001 `
  -T item_set=jk `
  -T seeds=1 `
  -T temperature=0
```

```powershell
inspect eval src/tasks/elicit_anchored.py `
  --model openai/gpt-4o `
  -T item_set=jk `
  -T seeds=1 `
  -T temperature=0

inspect eval src/tasks/elicit_anchored.py `
  --model openai/gpt-4o-mini `
  -T item_set=jk `
  -T seeds=1 `
  -T temperature=0
```

`seeds` is a historical compatibility name. In this implementation it creates
repeat labels; it is not passed to a random-number generator or model provider.
The portfolio run intentionally uses one repeat and temperature 0.

Analyze the newest successful J&K log:

```powershell
python scripts/analyze_jk.py
```

Or analyze a specific log and save a machine-readable summary:

```powershell
python scripts/analyze_jk.py logs/<run>.eval --output results/jk_summary.json
```

Build the fixed human-verification worksheet from the completed full runs:

```powershell
python scripts/build_human_audit.py
```

This writes a 20-output stratified review sample plus every parser exception to
`results/human_audit_2026-07-21.md` and a machine-readable JSON companion. A
human reviewer should compare each raw transcript with its parsed values and
complete the included checklist, name, timestamp, verdict, and notes.

Run the checks with:

```powershell
python -m pytest
```

For a no-cost smoke test:

```powershell
inspect eval src/tasks/elicit_anchored.py `
  --model mockllm/model `
  -T item_set=jk `
  -T seeds=1 `
  --limit 2
```

The mock model does not emit numeric intervals, so a parse score of zero is
expected; the smoke test only verifies that the task executes.

## Measures

- **Anchoring index:** `(median(high) - median(low)) / (high anchor - low anchor)`
- **Width delta:** anchored relative interval width minus control width
- **Human comparison:** Spearman correlation between model and published
  per-item anchoring indices
- **Comparative consistency:** agreement between the first-turn greater/less
  response and the model's own unanchored estimate

An anchoring index of 0 indicates no pull and 1 indicates estimates moving all
the way to the anchors. Negative width delta means the anchored response became
narrower.

## Scope and limitations

- The J&K bridge and 18-item staged taxon pilot have completed results. Both
  remain exploratory rather than powered model comparisons.
- Temperature 0 requests low-variance generation but does not guarantee
  identical output. Some reasoning models do not expose temperature controls.
- `seeds > 1` creates repeated requests, not independently seeded samples.
- Human anchoring values are group statistics; model values come from one
  model run per condition in the recommended configuration.
- Control and anchored conditions differ in conversation length, so measured
  effects may include some protocol-format influence.

## Repository map

- `src/tasks/elicit_anchored.py` — Inspect task and two-turn solver
- `src/anchoring_metrics.py` — anchoring and interval-width metrics
- `scripts/analyze_jk.py` — log extraction and compact analysis
- `scripts/build_human_audit.py` — reproducible raw-output verification sample
- `data/jk_items.yaml` — published J&K items and human indices
- `results/human_audit_2026-07-21.md` — human review worksheet
- `prompts/` — control, comparison, and estimation prompts
- `tests/` — focused correctness and dataset checks
- `R6_HANDOFF.md` — notes for the larger future taxon evaluation

## Optional harder taxon arm

Rebuild its inputs from the original R3 project with:

```powershell
python scripts/import_r3.py `
  --r3-root C:\Users\chaos\Projects\bird-taxonomy-evals `
  --baseline "results/latest_inspect/by_prompt.csv=2026-07-02" `
  --baseline "results/sonnet45_anchor_baseline/by_prompt.csv=2026-07-18"
```

The full 54-item arm would contain 270 samples and 540 calls per model with the
matched two-turn control. R7 starts with an 18-item exploratory stage: 90
samples and 180 calls per model, or 720 calls across four models. For example:

```powershell
inspect eval src/tasks/elicit_anchored.py `
  --model anthropic/claude-sonnet-4-5-20250929 `
  -T item_set=taxon `
  -T baseline_model=taxonomy-r3/claude-sonnet-4-5-20250929@2026-07-18 `
  -T subset_path=data/taxon_subset_r7.yaml `
  -T anchor_method=outside `
  -T anchor_strength=2 `
  -T matched_control=true `
  -T seeds=1 `
  -T temperature=0
```

The predeclared subset excludes items with collapsed anchors for any target
model. Fresh controls that drift outside their model-specific anchors are
flagged and excluded from the primary aggregate.
