# Do irrelevant numbers change an LLM's confidence?

## Summary

The finding from this series is a same-turn contradiction fork. In the two-step
anchoring protocol, models sometimes say “greater” or “less” on turn one and
then emit an interval on the opposite side of the anchor. Round 8 tested whether
clearer `TRUE_GREATER` / `TRUE_LESS` labels collapse that pattern. They do for
some models and not others: Sonnet 4.5 and Opus 4.5 went to zero contradictions,
while Haiku 4.5 and GPT-4o largely did not. Sonnet 5 was partial. High-side
asymmetry survived equalizing low/high anchor distance when labels stayed
ambiguous.

The abstract for the earlier arms is simpler: irrelevant anchors mostly did not
move these LLMs the way they move people. I adapted Jacowitz and Kahneman
(1995) in Inspect AI across Claude Sonnet 4.5, Claude Haiku 4.5, GPT-4o, and
GPT-4o mini on 15 published questions with unanchored controls and low/high
anchors framed as random numbers or analyst estimates. Relative to the J&K
human item-level mean of 0.484, model anchoring was much smaller. Separately,
within each model the median anchoring index was zero—so at least half the
items did not move—which is why nonzero means are fragile and why an apparent
analyst-source advantage did not survive baseline-bracketing. Intervals also
widened slightly rather than narrowing, against the false-confidence
hypothesis. A 30-year-old behavioral benchmark remains useful as a protocol
bridge, but it needs modernized stimuli and, after Round 8, model-specific
consistency checks.

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
- first-turn comparative consistency against the separate control p50;
- the number of items with nonzero anchor effects;
- whether the model's control estimate falls between the low and high anchors;
- Spearman correlation with published human item-level anchoring indices.

After the run, I also audited whether each first-turn comparison agreed with
the interval produced in the same conversation. This is distinct from the
original comparative-consistency measure.

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

## When the two turns disagree

Human review found cases where the categorical comparison and the subsequent
interval pointed in opposite directions. For example, a model could say that
the true answer was “greater” than a high anchor and then provide a p10–p90
interval entirely below that anchor.

Across the 240 anchored R6 responses:

- 192 comparisons, or 80.0%, agreed with the p50 produced in the same
  conversation;
- 29 responses, or 12.1%, placed the entire interval on the opposite side of
  the anchor from the first-turn answer;
- hard contradictions occurred in 17 of 60 high-arbitrary and 10 of 60
  high-analyst-source responses, compared with 2 of 60 low-arbitrary and none
  of the 60 low-analyst-source responses.

The high-versus-low asymmetry makes this more than a formatting footnote, but
the current run cannot identify its cause. A model may reverse the comparison's
referent, treat the forced one-word answer as a weak local output rather than a
stable commitment, reconsider the question on the second turn, or be influenced
by having generated the token “greater” or “less.” The data do not distinguish
among these explanations.

This finding also does not automatically invalidate the anchoring index. The
index is computed from the second-turn p50 estimates under low and high anchors,
not from the categorical answers. However, if producing “greater” or “less”
changes the following estimate, then part of the measured effect could come
from self-generated language rather than the numeric anchor alone. Round 8
tested the label-ambiguity piece. The next step is sham-token controls
(direction-neutral `ready`, forced-`greater`, and forced-`less`) to separate
token priming from reconsideration.

## Round 8: same-turn contradiction follow-up

Round 8 used an 8-item high-count taxon subset and a predeclared decision tree:

1. Contradictions collapse under `TRUE_GREATER` / `TRUE_LESS` → phrasing /
   subject-reversal artifact → methods critique.
2. Contradictions persist → genuine same-turn incoherence.
3. Partial collapse → report how much of the apparent effect was subject-
   reversal.

**Arm A** kept R7 outside anchors and replaced first-turn labels with
`TRUE_GREATER` / `TRUE_LESS`. **Arm B** kept ambiguous `greater` / `less` labels
but placed low/high anchors at equal distance from p50 (`matched_distance`) to
test whether the high-side contradiction skew was an artifact of uneven
outside-anchor lengths.

Whole-interval contradiction rates on the same 8 items:

| Model | R7 (ambiguous labels) | Arm A (`TRUE_*`) | Arm B (matched distance) |
|---|---|---|---|
| Claude Haiku 4.5 | 12/32 (38%) | 11/32 (34%) | 10/32 (31%) |
| GPT-4o mini | 4/32 (12%) | 2/32 (6%) | 3/32 (9%) |
| Claude Sonnet 4.5 | 12/32 (38%) | **0/32 (0%)** | 12/32 (38%) |
| GPT-4o | 12/32 (38%) | 10/32 (31%) | 13/32 (41%) |
| Claude Sonnet 5 | — | 5/30 (17%) | — |
| Claude Opus 4.5 | — | **0/32 (0%)** | — |

Sonnet 5 had a 95% parse rate on Arm A; the denominator is parsed anchored
comparisons.

**What this means.** The outcome is not one fork for all models. Sonnet 4.5 and
Opus 4.5 match outcome 1: under clearer labels, same-turn contradictions
disappear, so their R7 contradictions look like a comparative-phrasing artifact.
Haiku 4.5 and GPT-4o match outcome 2 more closely: clearer labels barely moved
the rate. Sonnet 5 is partial (17%, still high-side only).

Arm B did not remove the high-versus-low asymmetry when labels stayed
ambiguous. For Haiku, Sonnet 4.5, and GPT-4o, high anchors still produced most
of the contradictions after equalizing distance from p50. That asymmetry looks
positional, not an artifact of uneven outside-anchor lengths.

Machine-readable summaries are in `results/r8_*.json`. The frozen plan is
[`R8_CONTRADICTION_PLAN.md`](R8_CONTRADICTION_PLAN.md).

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

Five findings are worth carrying forward.

First, as a human comparison: the models anchored much less than the J&K sample.
Human item-level AI had a mean of 0.484 and median of 0.43; pooled and
per-model model effects were far smaller.

Second, as a within-model distributional fact: the median anchoring index was
zero in every model and provenance condition, so at least half the items did
not move. That zero inflation is what makes full-set means fragile. Plausible
framing affected a minority of cases, and the apparent provenance advantage did
not survive baseline-bracketing.

Third, the models did not reproduce the human item-level pattern. Human–AI rank
correlations were weak or negative except for a small positive correlation in
Sonnet's plausible condition. With 15 items and one response per condition,
these correlations are exploratory.

Fourth, anchoring did not create false precision in this run. Intervals stayed
similar or widened. One interpretation is that the extra context introduced
additional uncertainty. Another is that conversation structure—not anchoring
alone—changed the response. Round 7's matched two-turn control addresses part
of that protocol gap.

Fifth, the two turns should not be assumed to express one internally stable
judgment. Round 8 shows that some of the same-conversation contradictions are a
comparative-phrasing artifact and some are not; the remaining ambiguity between
token priming and reconsideration is the next experiment, not a side note.

## What the evaluation exposed

The project was useful even where the hypothesis was not supported.

- **Median-only reporting hid sparse effects.** I added mean and mean-absolute
  anchoring indices plus counts of nonzero item pairs.
- **Exact-string scoring was too brittle.** Punctuation normalization fixed the
  comparative-consistency metric.
- **Human review exposed cross-turn contradictions.** The original aggregate
  metric did not show when a first-turn answer was opposed by the entire
  interval generated immediately afterward.
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

I did not run the full anchored taxon arm. At 540 generations per model, the
four-model version would require 2,160 additional generations with the new
matched two-turn control.

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

1. Run 18 stratified items as an exploratory diagnostic, costing 720
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
- First-turn categorical answers can conflict with same-conversation intervals;
  the current data cannot determine whether this reflects referent ambiguity,
  token priming, reconsideration, or another generation effect.
- Control and treatment differ in conversation length.
- The power analysis uses the unfiltered, zero-inflated pilot and a normal
  approximation; it should be revised before a confirmatory run.
- Results generalize only to the tested prompts, models, and snapshots.

## Next iteration

**Next:** sham-token controls. Round 8 separated label ambiguity from residual
incoherence for some models, but it cannot tell token priming from
reconsideration. The load-bearing follow-up is a direction-neutral `ready` arm
plus forced-`greater` and forced-`less` arms on the same items and models.

Rounds 7 and 8 already covered the matched two-turn control, stronger anchors,
stratified taxon pilot, clearer comparative labels, and matched-distance
asymmetry check. After the sham-token arms, remaining design priorities:

1. Prefer `TRUE_GREATER` / `TRUE_LESS` for any future comparative-step arm where
   same-turn consistency matters, especially for models that collapsed under
   Round 8 Arm A.
2. Treat contradiction rates as model-specific rather than pooling a single
   protocol diagnosis across providers.
3. Separate timeless J&K items from time-sensitive historical stimuli.
4. Decide in advance whether the primary endpoint is plausible anchoring,
   arbitrary anchoring, or their difference.

The main lesson is that a useful evaluation does not need a positive headline.
This series found a model-heterogeneous contradiction fork, limited anchoring
relative to humans, sparse within-model movement that makes means fragile, no
evidence of false confidence, an aging-stimulus confound, and a clear next
protocol test.
