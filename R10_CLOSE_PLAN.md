# R10 confirmatory wrap-up

## Goal

Test whether the binder / non-binder split identified on the Round 8/9 taxon
subset **travels** to a new setting. A wrap-up that only reclassifies the same
8 items is post-hoc. This round predeclares a change and checks it on J&K.

## Cause claim (frozen)

The same-turn contradiction split is a **binding** problem, not token priming
and not a single phrasing bug for every model:

- **Binders** (Sonnet 4.5; Opus already clean on taxon): a sincere `TRUE_*`
  judgment constrains the later interval; ambiguous `greater`/`less` does not.
- **Non-binders** (Haiku 4.5, GPT-4o): the first-turn token does not constrain
  the interval, sincere or forced.

Round 9 ruled out directional token priming on the taxon subset. This round
does not retest priming.

## New setting

Same 15 Jacowitz & Kahneman items as Round 6, original human-calibrated
anchors, both provenances, one repeat, temperature 0. First-turn labels:
`TRUE_GREATER` / `TRUE_LESS`. Existing Round 6 logs are the ambiguous-label
baseline. Do **not** rerun `greater`/`less`.

Round 6 whole-interval contradictions (ambiguous labels, 60 anchored cells):

| Model | Rate | High / low |
|---|---|---|
| Claude Haiku 4.5 | 9/60 (15%) | 9/30 / 0/30 |
| Claude Sonnet 4.5 | 7/60 (12%) | 6/30 / 1/30 |
| GPT-4o | 6/60 (10%) | 6/30 / 0/30 |
| GPT-4o mini | 7/60 (12%) | 6/30 / 1/30 |

Held-out R7 taxon items were rejected as the test set: almost all contradictions
lived on the high-count 8 (Sonnet 4/40, GPT-4o 3/40 on the other 10). Floor
effect would fake a collapse.

## Predeclared prediction (lock before paid runs)

Primary pair:

1. **Sonnet 4.5 (binder):** whole-interval contradictions **drop hard** from
   7/60 toward 0.
2. **Haiku 4.5 (non-binder):** whole-interval contradictions **stay in the same
   ballpark** as 9/60 (do not collapse).

Read the 2×2:

| | Sonnet drops | Sonnet stays |
|---|---|---|
| **Haiku stays** | Split travels. Binding/non-binding is a portable protocol fact. | Binder story was taxon-subset-specific. |
| **Haiku drops** | `TRUE_*` is a general methods fix; “non-binder” was subset-specific. | Neither family generalizes; do not claim a wrap-up reason. |

Power is modest (7 and 9 events). This is an out-of-sample protocol test, not a
powered replication of the 12/32 taxon rates.

## Models (first paid run)

- `anthropic/claude-sonnet-4-5-20250929`
- `anthropic/claude-haiku-4-5-20251001`

Do not add GPT-4o unless the primary pair is ambiguous (both move a little).
Do not run Sonnet 5 sham as the headline of this round.

## Secondary (desk, not the fork classifier)

After the confirmatory arm is written against the table above:

- Arm A vs R9 `ready` p50 on the taxon subset (logs already exist).
- Optional timeless vs time-sensitive J&K sensitivity on Round 6 AI, with a
  codebook frozen before looking at split means. Not the R10 headline.

## Cost

15 items × 5 conditions (control + 4 anchored) = **75 samples / 135 generations
per model**. Pair: **270 generations**. Control stays the Round 6 single-turn
form so the anchored cells match the original J&K two-step protocol.

## Run command

```powershell
$env:PYTHONPATH = (Get-Location).Path

inspect eval src/tasks/elicit_anchored.py `
  --model anthropic/claude-sonnet-4-5-20250929 `
  -T item_set=jk `
  -T comparative_labels=true_greater_less `
  -T seeds=1 `
  -T temperature=0
```

Same for `anthropic/claude-haiku-4-5-20251001`.

## Definition of done

- This prediction unchanged after seeing results
- Both logs + machine-readable contradiction comparison vs Round 6
- Short write-up stating which cell of the 2×2 applied
- Tag `r10-close-v1` when frozen

## Out of scope

New first-turn manipulations, residual-incoherence experiments on persist
models, new high-count taxon items (unless this pair is ambiguous), Sonnet 5
sham as the primary result.
