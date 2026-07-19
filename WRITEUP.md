# Do irrelevant numbers change an LLM's confidence?

## Summary

I built a small behavioral evaluation to test whether irrelevant numerical
anchors change an LLM's estimate or its stated uncertainty. The evaluation
adapts the two-step anchoring procedure used by Jacowitz and Kahneman (1995):
first ask whether the true answer is greater or less than an anchor, then ask
for the model's own p10, p50, and p90 estimate.

I ran the evaluation with Claude Sonnet 4.5, Claude Haiku 4.5, GPT-4o, and
GPT-4o mini using Inspect AI. Each model received the same 15 published
questions under five conditions: an unanchored control plus low and high
anchors described as either random numbers or analyst estimates.

The main result was not broad anchoring. The median anchoring index was zero in
every model and provenance condition, meaning that at least half of the items
produced identical estimates under low and high anchors. Raw means were higher
when the number was attributed to an analyst, but that pattern was driven by a
small number of items and did not survive a baseline-bracketing sensitivity
check.

The run also challenged the original hypothesis that anchors would create false
confidence. Intervals generally widened slightly after anchoring instead of
narrowing. More broadly, it showed that a 30-year-old behavioral benchmark can
be useful as a protocol bridge while still needing modernized stimuli.

## Why this question?

LLMs are often asked to produce estimates under uncertainty. In realistic use,
those estimates rarely arrive in a vacuum: a user may mention a budget, quote
another analyst, or provide a speculative number before asking for a forecast.
If that number changes not only the model's answer but also how confident it
sounds, the effect matters for decision support.

Anchoring is well established in human judgment. The interesting engineering
question is whether a model's structured uncertainty estimates show an
analogous effect and whether the source of an anchor changes its influence.

This evaluation focuses on two outcomes:

1. **Location:** Does the model's p50 move toward the anchor?
2. **Width:** Does the model's p10–p90 interval become narrower or wider?

## Evaluation design

The J&K bridge arm uses 15 estimation questions and the original low and high
anchors reported by Jacowitz and Kahneman. This creates an interpretable bridge
to human results without claiming that a single model response is equivalent
to a human group statistic.

The stimuli date to 1995. Stable facts such as Mount Everest's height remain
reasonable comparison items, but quantities such as university staffing,
population, consumption, and institutional counts have changed. I therefore
report the complete set for fidelity and treat temporally stable, baseline-
bracketed cases as the more meaningful human comparison.

Every item has five conditions:

- **Control:** Ask directly for p10, p50, and p90.
- **Low arbitrary:** Present the low anchor as a random number.
- **High arbitrary:** Present the high anchor as a random number.
- **Low plausible:** Present the low anchor as an analyst estimate.
- **High plausible:** Present the high anchor as an analyst estimate.

Anchored conditions use two turns. The first asks for exactly “greater” or
“less.” The second asks for the model's own interval without repeating the
anchor. The control condition uses one turn.

The implementation is an Inspect AI task with:

- a programmatically generated factorial dataset;
- a two-turn solver for anchored conditions;
- strict parsing of ordered p10, p50, and p90 values;
- scorer metadata carrying the item, condition, anchor, provenance, direction,
  comparative answer, interval, and normalized width;
- an offline analysis script that reads Inspect `.eval` logs.

Each model run contained 75 samples and 135 model generations. Across four
models, the completed J&K experiment used 540 generations.

## Measures

The primary location measure is the two-anchor anchoring index:

`AI = (p50_high - p50_low) / (high_anchor - low_anchor)`

An index of 0 means the low and high anchors produced the same estimate. An
index of 1 means the estimates moved across the full distance between anchors.
Negative values indicate movement opposite the anchor.

Interval width is normalized by the p50 for linear-scale questions. Width delta
is anchored width minus control width, so a negative value would support the
false-confidence hypothesis.

The analysis also reports:

- parse rate;
- first-turn comparative consistency;
- the number of items with nonzero anchor effects;
- whether the model's control estimate falls between the low and high anchors;
- Spearman correlation with published human item-level anchoring indices.

## Results

The model summaries below describe the full 15-item historical stimulus set.
They are useful for showing exactly what happened under the original protocol,
but the raw means should not be interpreted as clean estimates of modern
human–AI differences.

### Claude Sonnet 4.5

Sonnet parsed all 75 intervals and produced first-turn comparisons consistent
with its own control estimate 85.0% of the time.

Its mean anchoring index was 0.198 for arbitrary anchors and 0.275 for plausible
anchors. Six of 15 arbitrary item pairs and five of 15 plausible pairs had
nonzero effects. Despite the higher plausible mean, the median remained zero in
both conditions because effects were concentrated in a minority of questions.

Median interval width increased by 0.038 under arbitrary anchors and 0.023 under
plausible anchors.

### Claude Haiku 4.5

Haiku parsed all intervals and reached 81.7% comparative consistency. It was the
least anchor-sensitive model in this run.

Mean anchoring indices were 0.044 for arbitrary anchors and 0.116 for plausible
anchors. Only two arbitrary and three plausible item pairs had nonzero effects.
Median width change was +0.009 for arbitrary anchors and zero for plausible
anchors.

### GPT-4o

GPT-4o parsed every interval and had the highest comparative consistency at
88.3%.

Its arbitrary-anchor mean was -0.044, indicating a small net contrast effect,
while its plausible-anchor mean was +0.096. Four of 15 items changed in each
provenance condition. Median interval-width changes were small and positive:
+0.008 and +0.003.

GPT-4o frequently answered “Greater.” or “Less.” with punctuation despite the
one-word instruction. This exposed a flaw in the first analysis pass, which
accepted only exact unpunctuated strings. I corrected the analyzer to normalize
these responses rather than misclassify them as missing.

### GPT-4o mini

GPT-4o mini parsed 74 of 75 intervals and had the lowest comparative consistency
at 73.2%. Its failed interval was `30 25 35`: correctly formatted but invalid
because the supposed p10 exceeded the p50.

It reacted on the most items: eight arbitrary and seven plausible pairs. Mean
anchoring indices were 0.058 and 0.242. It also widened its intervals the most,
with median deltas of +0.100 and +0.119.

## When a historical benchmark ages

The Berkeley female-professor question produced the clearest mismatch. Its
human-calibrated anchors were 25 and 130, while Sonnet's modern unanchored
estimate was 1,100. Both anchors were therefore “low” relative to the model's
belief. The resulting two-anchor index was 4.286 and heavily influenced the
raw mean, even though the setup was no longer analogous to J&K's calibrated
low/high comparison.

This was not only a Berkeley issue. Several original quantities are inherently
time-sensitive: UN membership, Chicago population, meat consumption, births,
gas usage, Berkeley bars, and California colleges. Their historical anchors
remain valid replication stimuli, but they are not automatically valid
contemporary calibration points.

For transparency, I retain all 15 items in the full-set result. I also ran a
sensitivity check that excluded each model-item case where the model's
unanchored p50 fell outside the human low/high anchor range. Forty-one of 60
model-item cases remained:

- arbitrary anchors: mean AI 0.103, median 0;
- plausible anchors: mean AI 0.056, median 0.

Under this check, the apparent plausible-provenance advantage disappears.
That makes the honest conclusion narrower: these models usually did not move,
and the nonzero effects were sparse, heterogeneous, and sensitive to stimulus
age.

## What the run suggests

Three findings are worth carrying forward.

First, the models anchored much less than the J&K human sample. Human item-level
AI had a mean of 0.484 and median of 0.43. The model medians were zero, including
after pooling across models. Plausible framing affected a minority of cases,
but the full-set mean overstated how typical that effect was.

Second, the models did not reproduce the human item-level pattern. Human–AI rank
correlations were weak or negative except for a small positive correlation in
Sonnet's plausible condition. With 15 items and one response per condition,
these correlations are exploratory.

Third, anchoring did not create false precision in this run. Intervals stayed
similar or widened. One interpretation is that the extra context introduced
additional uncertainty. Another is that conversation structure—not anchoring
alone—changed the response. A protocol-matched control is needed to distinguish
those explanations.

## What the evaluation exposed

The project was useful even where the hypothesis was not supported.

- **Median-only reporting hid sparse effects.** I added mean and mean-absolute
  anchoring indices plus counts of nonzero item pairs.
- **Exact-string scoring was too brittle.** Punctuation normalization fixed the
  comparative-consistency metric.
- **Strict interval validation was valuable.** It caught a substantive quantile
  ordering error from GPT-4o mini.
- **The repeat parameter was misleading.** The original `seeds` value created
  labels but did not seed model generation. The portfolio run now uses one
  repeat and documents the limitation.
- **The control is not protocol matched.** It uses one turn while anchored
  conditions use two, leaving a conversation-length confound.
- **Historical calibration can expire.** A fixed 1995 anchor may no longer sit
  above or below a current model's belief as intended.

These are the kinds of issues a smaller pilot should reveal before scaling an
evaluation.

## Harder taxon extension

The repository also contains a 54-item bird-taxonomy arm built from an earlier
calibration evaluation. These questions are more specialized and should reduce
the chance that models simply retrieve a memorized answer.

I imported the current item bank and model-specific baseline intervals for all
four target models. Sonnet 4.5 was absent from the original baseline run, so I
generated its missing 54-item baseline rather than substituting another model's
uncertainty estimates.

I did not run the full anchored taxon arm. At 486 generations per model, the
four-model version would require 1,944 additional generations.

## Power and staged sampling

I used the J&K item effects as pilot data for a planning calculation. Treating
the item as the experimental unit and averaging across the four fixed models:

- the full-set plausible-anchor effect suggests 26 items for 80% power if the
  taxon effect is equally strong;
- 45 items are needed if taxon retains 75% of the J&K effect;
- more than the full 54-item bank is needed if the effect is halved;
- the plausible-minus-arbitrary contrast requires about 51 items at the full
  pilot effect.

This calculation used the original full-set pilot before the temporal and
baseline-bracketing sensitivity analysis. It is therefore an optimistic
planning heuristic, not a final powered design. Taxon anchor strength is
configurable and should be chosen before rerunning the calculation. The
practical recommendation remains a staged design:

1. Run 18 stratified items as an exploratory diagnostic, costing 648
   generations across four models.
2. Check whether the effect transfers and whether new protocol flaws appear.
3. Expand to a predeclared 27-item set only if a pooled confirmatory result is
   still useful.

The 18-item stage is intentionally described as useful, not powered. That is
appropriate for the project's goal: learn quickly, improve the design, and
reserve larger runs for a stronger second iteration.

## Limitations

- There are only 15 J&K items and one response per condition.
- The four models are not release-matched, so this is not a clean provider
  comparison.
- Temperature 0 reduces sampling variation but does not guarantee identical
  outputs across providers.
- Human anchoring indices are group statistics; model values come from one
  response per condition.
- Several J&K quantities and their human-calibrated anchors are time-sensitive.
- Full-set means are sensitive to cases where both anchors fall on the same
  side of a model's baseline belief.
- Control and treatment differ in conversation length.
- The power analysis uses the unfiltered, zero-inflated pilot and a normal
  approximation; it should be revised before a confirmatory run.
- Results generalize only to the tested prompts, models, and snapshots.

## Next iteration

The next version should prioritize design improvements over raw scale:

1. Add a two-turn no-anchor control.
2. Separate timeless J&K items from time-sensitive historical stimuli.
3. Make anchor intensity explicit and ensure low/high anchors bracket each
   model's baseline.
4. Preselect a stratified 18-item taxon pilot and exclude collapsed anchors.
5. Preserve provenance as a factor, without assuming its pilot mean will
   replicate.
6. Analyze first-turn compliance and second-turn movement separately.
7. Decide in advance whether the primary endpoint is plausible anchoring,
   arbitrary anchoring, or their difference.
8. Run current frontier models only after the revised protocol survives the
   cheaper pilot.

The main lesson is that a useful evaluation does not need a positive headline.
This run found limited anchoring, no evidence of false confidence, an aging-
stimulus confound, and several concrete ways to improve the protocol.
