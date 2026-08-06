# LLM anchoring evaluations

Does an irrelevant number change what an LLM estimates — and how confident it
sounds when it says it?

This is a series of [Inspect AI](https://inspect.aisi.org.uk/) evaluations
adapting Jacowitz & Kahneman's (1995) two-step anchoring protocol to language
models: ask whether the answer is greater or less than an anchor, then ask the
model for its own p10/p50/p90 interval. Three rounds have completed across six
models.

The full narrative — motivation, design, findings, failures, next iteration —
is in [`WRITEUP.md`](WRITEUP.md).

## What it found

**1. The two turns don't always agree with each other.** This is the finding the
series ended up being about, and it wasn't what the evaluation was designed to
look for — a human audit of the transcripts surfaced it after the aggregate
metrics missed it entirely. Models sometimes answer "greater" on turn one, then
emit an interval lying *entirely on the other side* of the anchor. Across the
240 anchored Round 6 responses, 80.0% of comparisons agreed with the interval
produced in the same conversation, and 12.1% were whole-interval
contradictions. The contradictions were lopsided: 27 of 29 followed high
anchors.

Round 8 tested whether unambiguous `TRUE_GREATER` / `TRUE_LESS` labels collapse
the pattern. **The answer is model-dependent**, which is itself the result:

| Model | Ambiguous labels | `TRUE_*` labels |
|---|---|---|
| Claude Sonnet 4.5 | 12/32 (38%) | **0/32 (0%)** |
| Claude Sonnet 5 | 7/32 (22%) | 5/30 (17%) |
| Claude Haiku 4.5 | 12/32 (38%) | 11/32 (34%) |
| Claude Opus 4.5 | 1/32 (3%) | 0/32 (0%) |
| GPT-4o | 12/32 (38%) | 10/32 (31%) |
| GPT-4o mini | 4/32 (12%) | 2/32 (6%) |

Sonnet 4.5's contradictions were a comparative-phrasing artifact and vanished.
Haiku 4.5 and GPT-4o's did not — clearer labels barely moved them. Opus 4.5 had
almost nothing to collapse. So a single protocol diagnosis pooled across
providers would have been wrong for most of them.

A separate arm equalized the low/high anchor distance from p50 and the high-side
skew *survived* — it looks positional rather than an artifact of uneven anchor
lengths.

**2. These models anchor much less than people do.** On the 15 published J&K
items, the within-model median anchoring index was 0 in every model and every
provenance condition, against a human median of 0.43 (mean 0.484). At least half
the items didn't move at all. That zero-inflation is why full-set means are
fragile — and why an apparent "analyst estimates pull harder than random
numbers" effect did not survive a baseline-bracketing check.

The models also didn't anchor on the *same* items humans did: human–model rank
correlations were weak or negative.

**3. No evidence of false confidence.** The hypothesis going in was that
anchoring might narrow a model's stated uncertainty — confident and wrong.
Intervals stayed the same or got slightly *wider*. The mechanism isn't supported
here.

**Where it's heading:** a harder 18-item bird-taxonomy arm (Round 7) with
model-specific out-of-interval anchors, designed so models can't just retrieve a
memorized answer. Medians moved off zero for several models there, unlike the
J&K arm — suggestive that recall was masking the effect, but heterogeneous
across models and exploratory at 18 items. Next up is sham-token controls
(direction-neutral `ready`, forced-`greater`, forced-`less`) to separate token
priming from genuine reconsideration.

## What this is and isn't

It is a compact, honestly-reported evaluation series: a multi-turn Inspect task
with structured scoring metadata, a within-model control, a 2×2
direction/provenance design, a reproduction of the published anchoring-index
calculation, and a documented human audit of raw outputs.

It is **not** a powered behavioral study or a clean provider benchmark. One
response per condition, 15 J&K items, an 8-item Round 8 subset, and six models
that are not release-matched. The human comparison is exploratory. Limitations
are enumerated at the end of [`WRITEUP.md`](WRITEUP.md) rather than softened
here.

Several design flaws were found by running it, not by planning it — median-only
reporting hid sparse effects, exact-string scoring misclassified `Greater.` with
a period, a `seeds` parameter created repeat labels without seeding anything,
and 1995 stimuli have aged badly enough that some anchors no longer bracket a
modern model's belief. Those are written up as findings too.

## Rounds

| Round | Tag | What it is |
|---|---|---|
| 6 | `r6-jk-v1` | J&K bridge — 15 published items, original human anchors, unanchored control, arbitrary vs. analyst provenance |
| 7 | `r7-taxon-v1` | Staged taxon pilot — 18 bird-taxonomy items, model-specific outside anchors, matched two-turn control |
| 8 | `r8-contradiction-v1` | Contradiction follow-up — `TRUE_*` labels and matched-distance anchors |

Each tag is a frozen checkpoint, so a specific round can be checked out without
browsing branches. GitHub Release zips are also available.

Plans and results: [`RESULTS.md`](RESULTS.md) (Round 6 by model),
[`R7_TAXON_PLAN.md`](R7_TAXON_PLAN.md),
[`R8_CONTRADICTION_PLAN.md`](R8_CONTRADICTION_PLAN.md),
[`POWER_ANALYSIS.md`](POWER_ANALYSIS.md). Machine-readable summaries are under
`results/`.

## Measures

- **Anchoring index:** `(median(high) - median(low)) / (high anchor - low anchor)`.
  0 means no pull; 1 means estimates moved the full distance between anchors;
  negative means movement away from the anchor.
- **Width delta:** anchored relative interval width minus control width. Negative
  would support the false-confidence hypothesis.
- **Human comparison:** Spearman correlation between model and published
  per-item human anchoring indices.
- **Comparative consistency:** agreement between the first-turn greater/less
  answer and the model's own estimate.

## Setup

Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
```

Set the API key for whichever provider you're using. Don't commit it.

## Run

A J&K run is 75 samples and 135 model calls. The first pass deliberately used
lower-cost models to expose design flaws before spending on frontier models — a
pragmatic tier comparison, not a release-matched benchmark.

```powershell
inspect eval src/tasks/elicit_anchored.py `
  --model anthropic/claude-sonnet-4-5-20250929 `
  -T item_set=jk `
  -T seeds=1 `
  -T temperature=0
```

Swap `--model` for `anthropic/claude-haiku-4-5-20251001`, `openai/gpt-4o`, or
`openai/gpt-4o-mini` to reproduce the four-model Round 6 set.

`seeds` is a historical compatibility name: it creates repeat labels and is
**not** passed to a random-number generator or to the provider. The portfolio
runs use one repeat at temperature 0.

Analyze the newest successful J&K log, or a specific one:

```powershell
python scripts/analyze_jk.py
python scripts/analyze_jk.py logs/<run>.eval --output results/jk_summary.json
```

Rebuild the human-verification worksheet — a 20-output stratified review sample
plus every parser exception, with a checklist for the reviewer to sign:

```powershell
python scripts/build_human_audit.py
```

Tests, and a no-cost smoke test:

```powershell
python -m pytest

inspect eval src/tasks/elicit_anchored.py `
  --model mockllm/model `
  -T item_set=jk `
  -T seeds=1 `
  --limit 2
```

The mock model doesn't emit numeric intervals, so a parse score of zero is
expected — the smoke test only checks that the task executes.

### Taxon arm

Rebuild inputs from the upstream calibration project, then run the 18-item
stage (90 samples / 180 calls per model):

```powershell
python scripts/import_r3.py `
  --r3-root /path/to/bird-taxonomy-evals `
  --baseline "results/latest_inspect/by_prompt.csv=2026-07-02" `
  --baseline "results/sonnet45_anchor_baseline/by_prompt.csv=2026-07-18"

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

The subset is predeclared and excludes items with collapsed anchors for any
target model. Fresh controls drifting outside their model-specific anchors are
flagged and excluded from the primary aggregate. The full 54-item arm would be
270 samples and 540 calls per model.

## Repository map

- `src/tasks/elicit_anchored.py` — Inspect task and two-turn solver
- `src/anchoring_metrics.py` — anchoring and interval-width metrics
- `scripts/analyze_jk.py` — log extraction and analysis
- `scripts/analyze_contradiction.py` — Round 8 contradiction decomposition
- `scripts/build_human_audit.py` — reproducible raw-output verification sample
- `scripts/select_taxon_subset.py`, `scripts/select_contradiction_subset.py` —
  predeclared subset selection
- `data/jk_items.yaml` — published J&K items and human indices
- `prompts/` — control, comparison, and estimation prompts
- `results/` — machine-readable summaries and the human audit worksheet
- `tests/` — correctness and dataset checks
- `R6_HANDOFF.md` — notes toward the larger taxon evaluation

Raw Inspect `.eval` logs are excluded from version control as generated run
artifacts.

## License

MIT — see [`LICENSE`](LICENSE).
