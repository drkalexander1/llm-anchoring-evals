# R8 comparative-step contradiction follow-up

## Goal

Measure whether first-turn comparative judgments remain consistent with the
interval produced in the same conversation, and whether clearer labels collapse
the contradictions seen in R7.

## Predeclared decision tree

Freeze this before looking at Arm A results:

1. **Contradictions collapse under `TRUE_GREATER` / `TRUE_LESS`**
   - Interpretation: phrasing / subject-reversal artifact
   - Headline: methods critique of comparative-step anchoring protocols

2. **Contradictions persist at similar rates**
   - Interpretation: genuine same-turn belief incoherence
   - Headline: metacognition / commitment failure

3. **Partial collapse**
   - Interpretation: mixture
   - Headline: what fraction of the R7 anchoring effect was subject-reversal?
   - Report full-set AI vs consistent-pair-only AI from R7 and Arm A

Sham-token controls (`ready` / forced `greater` / forced `less`) are next:
they separate token priming from reconsideration after Round 8's label test.

## Arms

### Arm A — Disambiguation (primary)

- Same R7 outside anchors (`strength=2`)
- Same matched two-turn control
- First-turn labels: `TRUE_GREATER` / `TRUE_LESS`
- Subset: `data/contradiction_subset_r8.yaml` (high-count items)

### Arm B — Matched-distance low/high confirmation

- Original ambiguous `greater` / `less` labels
- Anchors from `anchor_method=matched_distance`
- Tests whether high-side contradiction asymmetry is positional

## Models (first paid run)

- `anthropic/claude-haiku-4-5-20251001`
- `openai/gpt-4o-mini`

## Immediate free analysis

```powershell
$env:PYTHONPATH = (Get-Location).Path
python scripts/analyze_contradiction.py --output results/r7_contradiction_decomposition.json
```

## Run commands

Arm A:

```powershell
$env:PYTHONPATH = (Get-Location).Path

inspect eval src/tasks/elicit_anchored.py `
  --model anthropic/claude-haiku-4-5-20251001 `
  -T item_set=taxon `
  -T baseline_model=taxonomy-r3/claude-haiku-4-5@2026-07-02 `
  -T subset_path=data/contradiction_subset_r8.yaml `
  -T anchor_method=outside `
  -T anchor_strength=2 `
  -T matched_control=true `
  -T comparative_labels=true_greater_less `
  -T seeds=1 `
  -T temperature=0
```

Arm B:

```powershell
inspect eval src/tasks/elicit_anchored.py `
  --model anthropic/claude-haiku-4-5-20251001 `
  -T item_set=taxon `
  -T baseline_model=taxonomy-r3/claude-haiku-4-5@2026-07-02 `
  -T subset_path=data/contradiction_subset_r8.yaml `
  -T anchor_method=matched_distance `
  -T anchor_strength=2 `
  -T matched_control=true `
  -T comparative_labels=greater_less `
  -T seeds=1 `
  -T temperature=0
```

Repeat both with `openai/gpt-4o-mini` and
`taxonomy-r3/gpt-4o-mini@2026-07-02`.

## Cost

For 8 items × 5 conditions × 2 turns × 2 models:

- Arm A: **160 generations**
- Arm B: **160 generations**
- Combined: **320 generations**

Smoke first with `--limit 3` on one model.

## Definition of done

- R7 contradiction decomposition written
- Arm A and Arm B scaffolds tested
- Decision tree unchanged after seeing results
- Arm A/B run on Haiku 4.5, GPT-4o mini, Sonnet 4.5, and GPT-4o
- Arm A run on Sonnet 5 and Opus 4.5
- Public write-up and `r8-contradiction-v1` freeze
