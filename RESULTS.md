# J&K bridge results

Run date: 2026-07-18  
Configuration: 15 items × 5 conditions, one repeat, temperature 0  
Models: Claude Sonnet 4.5, Claude Haiku 4.5, GPT-4o, GPT-4o mini

## Headline

All four models were mostly resistant to these anchors: the median anchoring
index was 0 for both arbitrary and plausible provenance in every model. The
mean results reveal sparse effects that the median intentionally suppresses.
Plausible analyst estimates produced more average pull than arbitrary random
numbers in all four models.

The intervals generally became slightly wider rather than narrower after an
anchor. This run therefore does not support the proposed false-confidence
mechanism, where anchoring would narrow the model's uncertainty interval.

## Model summaries

### Claude Sonnet 4.5

- Parse rate: 100%; comparative consistency: 85.0%
- Arbitrary anchors: mean AI 0.198; 6/15 items had a nonzero effect
- Plausible anchors: mean AI 0.275; 5/15 items had a nonzero effect
- Median width delta: +0.038 arbitrary, +0.023 plausible
- Human-AI Spearman: -0.480 arbitrary, +0.227 plausible

Sonnet showed the largest arbitrary-anchor pull and the largest plausible pull
after GPT-4o mini. The effects were concentrated in a minority of items.

### Claude Haiku 4.5

- Parse rate: 100%; comparative consistency: 81.7%
- Arbitrary anchors: mean AI 0.044; 2/15 items had a nonzero effect
- Plausible anchors: mean AI 0.116; 3/15 items had a nonzero effect
- Median width delta: +0.009 arbitrary, 0.000 plausible
- Human-AI Spearman: -0.127 arbitrary, -0.449 plausible

Haiku was the least anchor-sensitive model in this run.

### GPT-4o

- Parse rate: 100%; comparative consistency: 88.3%
- Arbitrary anchors: mean AI -0.044; 4/15 items had a nonzero effect
- Plausible anchors: mean AI 0.096; 4/15 items had a nonzero effect
- Median width delta: +0.008 arbitrary, +0.003 plausible
- Human-AI Spearman: +0.005 arbitrary, -0.269 plausible

GPT-4o was largely stable. Its negative arbitrary mean indicates a small net
contrast effect rather than pull toward the random anchors.

### GPT-4o mini

- Parse rate: 98.7%; comparative consistency: 73.2%
- Arbitrary anchors: mean AI 0.058; 8/15 items had a nonzero effect
- Plausible anchors: mean AI 0.242; 7/15 items had a nonzero effect
- Median width delta: +0.100 arbitrary, +0.119 plausible
- Human-AI Spearman: -0.223 arbitrary, -0.335 plausible

GPT-4o mini was the least instruction-consistent and reacted on the most items.
Plausible anchors produced substantial average pull, but its intervals widened
the most. Its single parse failure was a non-monotonic control interval
(`30 25 35`) rather than a formatting failure.

## Interpretation

The clearest signal is provenance sensitivity: every model had a more positive
mean anchoring index when the same number was attributed to an analyst instead
of a random generator. This pattern is exploratory because there are only 15
items and one response per condition.

The models did not reproduce the human item-level pattern. Human-AI rank
correlations were weak or negative, except for a small positive correlation in
Sonnet's plausible condition. These estimates are too noisy for a claim of
human similarity or dissimilarity.

## Design lessons for the next iteration

1. Keep provenance as a factor; it produced the most consistent cross-model
   difference.
2. Increase anchor intensity or choose less memorized questions. Most item
   pairs had identical low- and high-anchor estimates.
3. Add a protocol-matched two-turn control to separate anchoring from the extra
   conversational turn.
4. Add repeated stochastic samples only when they are genuinely provider-seeded
   or sampled at a nonzero temperature.
5. Retain strict interval validation: it caught a substantive ordering error
   that a formatting-only parser would have accepted.

Machine-readable summaries are available under `results/`. Raw Inspect logs are
excluded from version control because they are generated run artifacts.
