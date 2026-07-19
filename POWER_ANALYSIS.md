# Taxon-arm power analysis

This analysis uses the completed 15-item J&K runs as pilot data. The item is the
experimental unit. Effects are averaged across the four fixed models before
estimating a one-sided one-sample mean test at α = .05.

> **Planning estimate only:** These calculations use the complete historical
> stimulus set, including cases where the 1995 anchors do not bracket a modern
> model's baseline. The estimates are intentionally retained as an initial
> sizing exercise and should be recalculated after the next anchor design is
> fixed.

## Results

- Arbitrary-anchor effect: standardized effect 0.519; 23 items for 80% power.
- Plausible-anchor effect: standardized effect 0.495; 26 items for 80% power.
- Plausible-minus-arbitrary contrast: standardized effect 0.349; 51 items for
  80% power.

These figures assume the taxon effect is as large as the J&K pilot effect. If
taxon effects retain only 75% of the pilot magnitude, the plausible endpoint
requires 45 items. At 50% retention, it requires 101 items, which exceeds the
entire 54-item bank.

Model-specific estimates are substantially less powered. Within the 54-item
bank, 80% power is reached only for:

- GPT-4o mini plausible anchoring: 18 items
- Haiku 4.5 plausible anchoring: 32 items
- GPT-4o plausible anchoring: 45 items
- GPT-4o provenance contrast: 30 items
- GPT-4o mini provenance contrast: 40 items

Sonnet's pilot variance makes its individual endpoints require more than 54
items. A small taxon run therefore supports a cross-model exploratory result,
not robust claims about every model separately.

## Recommendation

Use a staged design:

1. Run 18 preselected, stratified taxon items as an exploratory diagnostic.
   This costs 648 calls across four models.
2. Use the run to identify prompt failures, collapsed anchors, and whether the
   taxon effect transfers at all.
3. If a confirmatory pooled effect is still worthwhile, expand the predeclared
   sample to 27 items (972 cumulative calls). This slightly exceeds the
   optimistic 26-item estimate.
4. Do not claim the provenance contrast is powered unless approximately 51
   items are run.

The 18-item stage is intentionally described as useful rather than powered. It
matches the portfolio objective: expose flaws cheaply before spending on a
larger or harder evaluation.

## Caveats

- The pilot has only 15 items and a zero-inflated effect distribution.
- The default verbalized taxon anchors are mild, but taxon anchor strength is
  configurable and has not yet been selected.
- The full-set J&K pilot is outlier-sensitive because some historical anchors
  no longer bracket modern model baselines.
- Averaging across four fixed models reduces variance but supports inference
  only about this model set.
- The normal approximation is a planning heuristic, not a preregistered test.

Full model-level estimates and 80%/90% sensitivity calculations are stored in
`results/power_analysis.json`. Reproduce them with:

```powershell
python scripts/power_analysis.py
```
