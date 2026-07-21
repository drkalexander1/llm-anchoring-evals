# R7 taxon anchoring follow-up

## Goal

Test anchoring on harder, specialized bird-taxonomy questions after the J&K
pilot showed sparse effects and aging historical stimuli.

R7 is a direct continuation rather than a human replication. It uses each
model's own prior taxon interval to construct low and high anchors, making the
intervention meaningful relative to that model's baseline belief.

## Predeclared pilot

- **Models:** Claude Sonnet 4.5, Claude Haiku 4.5, GPT-4o, GPT-4o mini
- **Items:** 18 from `data/taxon_subset_r7.yaml`
- **Strata:** 9 genus, 5 family, 4 order
- **Genus mix:** 5 well-known, 4 obscure
- **Conditions:** control, low/high arbitrary, low/high analyst-source
- **Repeats:** one
- **Temperature:** zero
- **Status:** exploratory diagnostic, not a separately powered model comparison

The subset is selected deterministically with seed `20260720`. Items are
eligible only when all four models have nondegenerate low and high anchors.

## Anchor design

R7 uses explicit out-of-interval anchors:

```text
low  = p50 - strength × (p50 - p10)
high = p50 + strength × (p90 - p50)
```

The predeclared strength is `2.0`. Therefore, an R3 baseline of
`220 / 240 / 260` produces anchors of `200 / 280`.

This is deliberately stronger than R6's p15/p85 interpolation. Unreasonable
values are intentional: anchoring does not require the number to be credible.
Anchor strength is stored in every sample and should not be changed after
examining R7 results.

## Matched control

All five conditions use two model generations:

1. Control says `ready`; anchored conditions answer `greater` or `less`.
2. Every condition receives the same interval-estimation prompt.

This balances conversation length. It does not make the control semantically
identical to the comparative task, so the remaining difference is documented.

## Cost

- 18 items × 5 conditions = 90 samples per model
- Every sample uses two generations = 180 generations per model
- Four models = **720 generations total**

The previous 648-call estimate assumed a single-turn control and no longer
applies.

## Endpoints

### Primary

Pooled analyst-source AI across the four fixed models:

`AI = (p50_high - p50_low) / (high_anchor - low_anchor)`

Report the item-level mean, median, mean absolute AI, and the number of nonzero
item effects. The mean is not reported without the median and item count.

### Secondary

- Arbitrary-anchor AI
- Analyst-source-minus-arbitrary AI difference
- Relative interval-width change versus matched control
- First-turn comparative consistency
- Results by genus/family/order and genus familiarity

The provenance contrast is exploratory; the 18-item stage is not powered for
that endpoint.

## Exclusions and sensitivity checks

Predeclare these before running:

1. Exclude a condition from interval metrics if p10/p50/p90 cannot be parsed or
   are not monotonic.
2. Exclude an item-model AI when low and high anchors are equal.
3. Flag and exclude an item-model AI from the primary aggregate when the fresh
   R7 control p50 is not strictly between its low and high anchors.
4. Report all exclusions and their raw responses.
5. Report a full-set descriptive result beside the valid-baseline primary
   result so exclusions remain transparent.

## Run commands

Run from the repository root after loading `.env`.

```powershell
$env:PYTHONPATH = (Get-Location).Path

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

Repeat with:

- `anthropic/claude-haiku-4-5-20251001` and
  `taxonomy-r3/claude-haiku-4-5@2026-07-02`
- `openai/gpt-4o` and `taxonomy-r3/gpt-4o@2026-07-02`
- `openai/gpt-4o-mini` and `taxonomy-r3/gpt-4o-mini@2026-07-02`

## Execution sequence

1. Run one control and one anchored sample per model as a smoke test.
2. Confirm the control acknowledgement and all interval parsing.
3. Run the complete 18-item set on the four models.
4. Export item-level effects and apply the predeclared exclusions.
5. Review distributions before writing aggregate claims.
6. Update the public write-up with R7 as a separate section.
7. Publish an `r7-taxon-v1` release.

Do not expand beyond 18 items this week based on an encouraging interim mean.
Any 27-item continuation should be a separately declared extension.

## Definition of done

- Four successful 90-sample Inspect logs
- Parse and exclusion audit
- Machine-readable model and pooled summaries
- Full-set and valid-baseline sensitivity results
- Updated README and R7 write-up
- Tests passing and no credentials or raw logs committed
