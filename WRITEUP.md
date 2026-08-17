# Do irrelevant numbers change an LLM's confidence?

## Summary

The finding from this series is a same-turn contradiction fork, plus a negative
result on one clean mechanism explanation for it. In the two-step anchoring
protocol, models sometimes say “greater” or “less” on turn one and then emit an
interval on the opposite side of the anchor. Round 8 tested whether clearer
`TRUE_GREATER` / `TRUE_LESS` labels collapse that pattern. They do for some
models and not others: Sonnet 4.5 fell from 12/32 to 0/32, Haiku 4.5 and GPT-4o
barely moved, and Sonnet 5 was partial (7/32 → 5/30). Opus 4.5 was already near
zero under ambiguous labels on this subset (1/32 → 0/32). High-side asymmetry
survived equalizing low/high anchor distance when labels stayed ambiguous.

Round 9 then asked whether forcing the first-turn token itself moves the later
estimate (token priming). On the same 8-item subset, forced `TRUE_GREATER` and
`TRUE_LESS` did **not** pull p50 in opposite directions relative to a matched
`ready` arm. Medians of the shift were zero for every model; means were sparse
and often ordered the wrong way for priming. So directional commitment to the
uttered token is not a good account of the two-step effects measured here.

Round 10 asked whether the binder / non-binder split was an artifact of the
8-item taxon subset. On the original 15 J&K items, `TRUE_*` labels dropped
Sonnet 4.5 from 7/60 to 2/60 and left Haiku 4.5 at 9/60 → 11/60. The split
travels: clearer labels are a portable fix for Sonnet-style binding failures,
not a general methods patch.

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
bridge, but it needs modernized stimuli and, after Rounds 8–10, model-specific
consistency checks rather than a single pooled protocol story.

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

Across the 240 anchored Round 6 (J&K bridge) responses—a different arm from
the Round 7 taxon pilot used later in Round 8:

- 192 comparisons, or 80.0%, agreed with the p50 produced in the same
  conversation;
- 29 responses, or 12.1%, placed the entire interval on the opposite side of
  the anchor from the first-turn answer;
- hard contradictions occurred in 17 of 60 high-arbitrary and 10 of 60
  high-analyst-source responses, compared with 2 of 60 low-arbitrary and none
  of the 60 low-analyst-source responses.

The high-versus-low asymmetry makes this more than a formatting footnote.
Candidate causes include reversing the comparison’s referent, treating the
one-word answer as a weak local output, reconsidering on the second turn, or
being pulled by the uttered token. Round 8 tested label ambiguity; Round 9
tested token priming (see below). Neither yields a single pooled explanation.

This finding also does not automatically invalidate the anchoring index. The
index is computed from the second-turn p50 estimates under low and high anchors,
not from the categorical answers. Round 9’s sham arms argue against a simple
“said greater, therefore estimated higher” contamination pathway on the later
taxon subset; they do not by themselves rewrite every Round 6 index.

## Round 8: same-turn contradiction follow-up

Round 8 used an 8-item high-count taxon subset and a predeclared decision tree:

1. Contradictions collapse under `TRUE_GREATER` / `TRUE_LESS` → phrasing /
   subject-reversal artifact → methods critique.
2. Contradictions persist → genuine same-turn incoherence.
3. Partial collapse → report how much of the apparent effect was subject-
   reversal.

**Arm A** kept Round 7 outside anchors and replaced first-turn labels with
`TRUE_GREATER` / `TRUE_LESS`. **Arm B** kept ambiguous `greater` / `less` labels
but placed low/high anchors at equal distance from p50 (`matched_distance`) to
test whether the high-side contradiction skew was an artifact of uneven
outside-anchor lengths.

The frozen plan locked the first paid Arm A/B runs to Haiku 4.5 and GPT-4o mini
and deferred expansion until the fork was classified. After that locked pair
showed persistence rather than collapse, the same arms were extended to Sonnet
4.5 and GPT-4o, then ambiguous-label baselines and Arm A to Sonnet 5 and Opus
4.5.

Whole-interval contradiction rates on the same 8 items:

| Model | Ambiguous labels | Arm A (`TRUE_*`) | Arm B (matched distance) |
|---|---|---|---|
| Claude Haiku 4.5 | 12/32 (38%) | 11/32 (34%) | 10/32 (31%) |
| GPT-4o mini | 4/32 (12%) | 2/32 (6%) | 3/32 (9%) |
| Claude Sonnet 4.5 | 12/32 (38%) | **0/32 (0%)** | 12/32 (38%) |
| GPT-4o | 12/32 (38%) | 10/32 (31%) | 13/32 (41%) |
| Claude Sonnet 5 | 7/32 (22%) | 5/30 (17%) | — |
| Claude Opus 4.5 | 1/32 (3%) | **0/32 (0%)** | — |

Rates are whole-interval contradictions on the same 8-item subset. For Haiku,
Sonnet 4.5, GPT-4o, and GPT-4o mini, the ambiguous-label column is the Round 7
taxon-pilot logs (90 samples per model) filtered to those 8 items—not the
Round 6 J&K bridge audit above. For Sonnet 5 and Opus 4.5, it is a matched
Round 8 rerun with `greater` / `less`, outside anchors, and the matched
two-turn control. Sonnet 5 Arm A had a 95% parse rate; that denominator is
parsed anchored comparisons (30 rather than 32). Percentages are rounded.

**What this means.** The outcome is not one fork for all models. Sonnet 4.5 is
the clean outcome-1 case: 12/32 under ambiguous labels to **0/32** under
`TRUE_*`, so its Round 7 contradictions look like a comparative-phrasing
artifact. Haiku 4.5 and GPT-4o match outcome 2 more closely: clearer labels
barely moved the rate. Sonnet 5 is partial (7/32 → 5/30), still high-side only.
Opus 4.5 was already nearly contradiction-free under ambiguous labels on this
subset (1/32) and stayed at 0/32 under `TRUE_*`—so Arm A does not show a Sonnet
4.5-style collapse for Opus; there was almost nothing to collapse.

Arm B did not remove the high-versus-low asymmetry when labels stayed
ambiguous. For Haiku, Sonnet 4.5, and GPT-4o, high anchors still produced most
of the contradictions after equalizing distance from p50. That asymmetry looks
positional, not an artifact of uneven outside-anchor lengths.

Machine-readable summaries are in `results/r8_*.json` (including
`results/r8_r7style_sonnet5_opus45.json`). The frozen plan is
[`R8_CONTRADICTION_PLAN.md`](R8_CONTRADICTION_PLAN.md).

## Round 9: sham-token controls

Round 8 established that clearer `TRUE_GREATER` / `TRUE_LESS` labels collapse
same-turn contradictions for some models and not others. What it could not
establish is whether the first-turn token *itself* moves the second-turn
estimate — whether emitting “greater” then pulls the estimate up because the
model said so. If that were true, part of what Rounds 6–7 measured as anchoring
could be self-generated language rather than the numeric anchor.

Round 9 tests that directly. Each arm is two turns of matched length, on the
same 8-item high-count taxon subset as Round 8, with outside anchors at
`strength=2` and both provenances retained:

- **ready** — direction-neutral acknowledgement, then the standard estimate
  prompt (reference condition).
- **forced TRUE_GREATER** — instruct the model to emit that token regardless of
  belief, then estimate.
- **forced TRUE_LESS** — same, opposite token.

The forced arms are shams: the token is not a sincere comparative judgment, so
any directional effect on the estimate is attributable to having uttered it.

### How to read this section

The primary result is eliminating a hypothesis. That is the intended use of the
design. Where a mechanism is ruled out, the space of explanations for earlier
two-step effects narrows; it does not by itself invent a new positive mechanism.

### Predeclared branches

Frozen in [`R9_SHAM_TOKEN_PLAN.md`](R9_SHAM_TOKEN_PLAN.md) before paid runs:

1. **Token priming** — forced-greater and forced-less pull p50 in opposite
   directions relative to `ready`.
2. **Residual incoherence** — forced arms match `ready` on location; contradictions
   persist where they did under Round 8 Arm A.
3. **Model-heterogeneous** — mixed; report per model; no pooled mechanism claim.

Stage 1 locked Haiku 4.5 and GPT-4o (the clear Round 8 persist cases). After
that pair was classified, Stage 2 added Sonnet 4.5, Opus 4.5, and GPT-4o mini.
Each model contributed 96 samples (32 per first-turn arm). Sonnet 5 was not run
in Round 9.

### Results

Mean signed p50 shift relative to `ready` (raw species-count units). Every
**median** shift was 0:

| Model | Forced TRUE_GREATER | Forced TRUE_LESS |
|---|---|---|
| Claude Haiku 4.5 | +0.16 | +1.34 |
| Claude Sonnet 4.5 | −1.84 | −1.53 |
| Claude Opus 4.5 | +4.66 | +6.94 |
| GPT-4o | −1.78 | −2.72 |
| GPT-4o mini | +5.31 | +5.22 |

Share of cells with no p50 change at all vs `ready`:

| Model | Forced GREATER | Forced LESS |
|---|---|---|
| Claude Haiku 4.5 | 38% | 44% |
| Claude Opus 4.5 | 62% | 66% |
| Claude Sonnet 4.5 | 75% | 72% |
| GPT-4o | 81% | 75% |
| GPT-4o mini | 78% | 81% |

Whole-interval contradiction rates (interval on the wrong side of the
*first-turn token*). For forced arms the token is imposed; for Round 8 Arm A it
was a sincere `TRUE_*` judgment:

| Model | Round 8 Arm A (sincere) | R9 forced GREATER | R9 forced LESS |
|---|---|---|---|
| Claude Haiku 4.5 | 11/32 (34%) | 11/32 (34%) | 16/32 (50%) |
| GPT-4o | 10/32 (31%) | 16/32 (50%) | 16/32 (50%) |
| GPT-4o mini | 2/32 (6%) | 2/32 (6%) | 4/32 (12%) |
| Claude Sonnet 4.5 | 0/32 (0%) | 14/32 (44%) | 16/32 (50%) |
| Claude Opus 4.5 | 0/32 (0%) | 8/32 (25%) | 13/32 (41%) |

Machine-readable summary: `results/r9_sham_all_models_summary.json`.

### Token priming is not supported

Token priming predicts that forced-GREATER p50 shifts exceed forced-LESS shifts
(relative to `ready`). They do not, for four of five models.

Haiku, Sonnet 4.5, and Opus all estimate *higher* after forced LESS than after
forced GREATER (wrong order for priming). GPT-4o mini’s GREATER vs LESS gap is
only 0.09 in the priming direction. Only GPT-4o shows the predicted ordering
(GREATER mean shift less negative than LESS), and even there medians are zero
and most cells do not move.

So this round does **not** support directional commitment to the uttered token
as an account of second-turn location on this subset. That removes one
contamination pathway that Round 6 had left open for two-step protocols. It does
**not** automatically sanitize every Round 6/7 anchoring index (different items,
and sincere vs forced first turns are not the same manipulation); it does say
the simple “said greater, therefore estimated higher” story fails here.

### What the forced arms did instead

Within each model, **both** forced arms tend to shift mean p50 in the **same**
direction relative to `ready` — up for Haiku, Opus, and GPT-4o mini; down for
Sonnet 4.5 and GPT-4o. Whatever the forced turn does, it is not mainly a
function of which token was emitted. The sign looks model-specific.

Median zero is not “the manipulation did nothing.” Haiku moves on a majority of
cells (about 56–62% nonzero); the other models move on roughly 19–38%. Nonzero
jumps are coarse integers (median |Δ| often 4–20 species), matching the Round 7
pattern that taxon p50s on this subset are sticky integers rather than smooth
beliefs. Movements cancel across items, so aggregates look inert while
item-level records are noisy — the same aggregate-vs-transcript lesson as
earlier rounds.

### Residual incoherence: uneven

For Haiku, forced-GREATER contradictions match sincere Round 8 Arm A exactly
(11/32): persistence after removing both label ambiguity and sincere token
choice. GPT-4o rises from 10/32 to 16/32 under either forced token — less
coherent when the token is insincere. GPT-4o mini stays low.

Sonnet 4.5 and Opus 4.5 are different: sincere Arm A was 0/32, but forced arms
produce many “contradictions.” That is expected if the model ignores an imposed
token and estimates from the question — the interval then routinely disagrees
with the sham label. Those rates are not evidence that sincere Arm A collapse
reversed; they show the forced-token consistency metric is measuring something
else for models that already refused to contradict under sincere `TRUE_*`.

### Which branch applied

**Branch 3, model-heterogeneous.** Sign of mean shift flips across models;
non-moving share spans 38–81%; contradiction response to an insincere token
differs sharply between persist models (Haiku/GPT-4o) and collapse models
(Sonnet/Opus). No single mechanism statement covers the set.

Together with Round 8, two independent manipulations both favor
model-specific protocol diagnoses over a pooled provider claim.

### Secondary readout: anchoring index by sham arm

Under plausible-provenance anchors, mean AI was higher under `ready` than under
either forced arm for Haiku (0.363 vs 0.198 / 0.214) and GPT-4o (0.130 vs 0.057
/ 0.064). Arbitrary-provenance AI is not consistent across forced arms. One
candidate reading is that a forced token substitutes for engagement with the
anchor. That is means-only on 32 cells per arm and is recorded as a hypothesis,
not a result.

### Round 9 limitations

- **`ready` is the reference for every Δp50.** These data alone cannot separate
  “forced arms moved” from “`ready` sits off-center.” Comparing forced p50s to
  Round 8 Arm A p50s on the same cells would help; that contrast is not the
  primary table above.
- **Means are in raw item units.** Opus and GPT-4o mini combine high zero shares
  with large means — leverage from a minority of big jumps. Do not quote those
  means as standardized effect sizes.
- **Coarseness.** On this high-count subset, p50s are integers; nonzero moves
  jump by multiple species. That limits sensitivity to tiny priming but does not
  manufacture the high exact-zero rates (those are repeated identical integers).
- Eight items, one response per cell, five Round 9 models, not release-matched.
  Exploratory throughout.

## Round 10: confirmatory wrap-up

Rounds 8–9 identified a binder / non-binder split on one 8-item taxon subset.
That is not enough to claim a reason. Round 10 predeclared a change on a
**new setting** — the original 15 J&K items from Round 6 — and checked it.

Frozen in [`R10_CLOSE_PLAN.md`](R10_CLOSE_PLAN.md) before paid runs:

- **Sonnet 4.5 (binder):** whole-interval contradictions drop hard from 7/60
  toward 0 under `TRUE_*`.
- **Haiku 4.5 (non-binder):** the rate stays in the same ballpark as 9/60.

Existing Round 6 logs are the ambiguous-label baseline. Same items, anchors,
provenances, and two-turn anchored protocol; only the first-turn contract
changes. Held-out R7 taxon items were rejected as the test set: almost all of
the original contradictions lived on the high-count 8, so a “collapse” there
could have been a floor effect.

### Results

| Model | Round 6 (`greater`/`less`) | Round 10 (`TRUE_*`) |
|---|---|---|
| Claude Sonnet 4.5 | 7/60 (12%), high 6/30 | **2/60 (3%)**, high 1/30 |
| Claude Haiku 4.5 | 9/60 (15%), high 9/30 | **11/60 (18%)**, high 10/30 |

Parse rate 100% on both 75-sample runs. Machine-readable summary:
`results/r10_jk_true_contradiction.json`.

### Which cell of the 2×2 applied

**Sonnet drops, Haiku stays.** The split travels off the taxon subset.

Sonnet 4.5 is not the taxon-style 12/32 → 0/32. Seven events became two, still
mostly high-side. That is a real drop toward zero on modest counts, not a
clean wipe. Haiku did not collapse; it ticked up. So `TRUE_*` is a portable
fix for Sonnet-style binding failures, not a general methods patch for
same-turn incoherence.

GPT-4o was not run. The plan added it only if the primary pair was ambiguous.
It was not.

### Secondary: Sonnet 5 sham

Same R9 arms on the 8-item taxon subset. Parse rate 97.9% (94/96). Arm A was
5/30 (17%), all high-side.

| Arm | Mean Δp50 vs `ready` | Exact zeros | Forced-token contradictions |
|---|---|---|---|
| Forced TRUE_GREATER | −1.45 | 68% | 11/32 (34%) |
| Forced TRUE_LESS | +0.43 | 63% | 15/31 (48%) |

Median Δp50 is 0. Forced GREATER is *lower* than forced LESS, so token priming
is the wrong order here too. Forced-token “contradictions” jump relative to
sincere Arm A, the same pattern as Sonnet 4.5 (0/32 sincere → 14–16/32 sham):
the model mostly ignores an imposed token. Call it a **partial binder** — not
Haiku’s 11/32 matching Arm A exactly.

Machine-readable: `results/r10_sham_all_models_summary.json`.

### Secondary: timeless vs time-sensitive J&K items

Frozen codebook [`data/jk_temporal_split.yaml`](data/jk_temporal_split.yaml)
(7 timeless, 8 time-sensitive) before looking at split means. This is not the
bracketing check below. Human item-level AI is similar on both subsets (0.46
vs 0.51). Model means are not:

| Model | Timeless plaus. mean AI | Aging plaus. mean AI |
|---|---|---|
| Claude Haiku 4.5 | 0.000 | 0.217 |
| Claude Sonnet 4.5 | 0.013 | 0.503 |
| GPT-4o | 0.145 | 0.053 |
| GPT-4o mini | 0.006 | 0.448 |

Medians are 0 on the timeless set for every model. Arbitrary-provenance means
are also near zero on timeless items. GPT-4o is the exception on aging
(near-zero there too). So the sparse full-set means were mostly aging
stimuli, not a small timeless anchoring effect that happened to look like
Berkeley. Humans in 1995 anchored on both kinds of item; these models did not.

`results/r10_jk_temporal_split.json`.

### Round 10 limitations

- Seven and nine events are a weak signal. This is an out-of-sample protocol
  test, not a powered replication of the taxon rates.
- Confirmatory `TRUE_*` is two models on J&K. It does not classify Opus,
  GPT-4o, or mini on that setting, and it does not explain *why* Haiku fails
  to bind.
- Sonnet 5 sham had two parse failures (denominator 31 on `ready` / forced
  LESS). Forced-token contradictions are not sincere Arm A.
- The temporal split is 7 vs 8 items, one response per cell. Exploratory.
  Cat speed is locked timeless (biology); UN members are locked time-sensitive.
- J&K still uses the unmatched single-turn control on the unanchored arm;
  the contradiction comparison uses only the two-turn anchored cells.

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
A separate Round 10 split, using a predeclared timeless vs time-sensitive
codebook rather than each model’s baseline, reaches the same qualitative
point: model means sit on the aging items; timeless medians are 0.

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
judgment. Round 8 shows that some same-conversation contradictions are a
comparative-phrasing artifact and some are not. Round 9 then rules out a clean
token-priming account of second-turn location on this subset: forced
`TRUE_GREATER` / `TRUE_LESS` do not pull p50 in opposite directions relative to
`ready`. Round 10 then showed that the binder / non-binder split is not a
taxon-subset artifact: on J&K, Sonnet 4.5 dropped under `TRUE_*` and Haiku did
not. Residual same-turn incoherence remains model-specific.

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
- The series now spans six models that are not release-matched, so this is not
  a clean provider comparison.
- Round 8's headline contradiction rates rest on an 8-item high-count subset
  with one response per cell (typically 32 anchored comparisons per
  model-arm; 30 for Sonnet 5 Arm A after parse failures). That is exploratory,
  not a powered consistency study.
- Temperature 0 reduces sampling variation but does not guarantee identical
  outputs across providers; some newer Claude models omit temperature.
- Human anchoring indices are group statistics; model values come from one
  response per condition.
- Several J&K quantities and their human-calibrated anchors are time-sensitive.
- Full-set means are sensitive to cases where both anchors fall on the same
  side of a model's baseline belief.
- First-turn categorical answers can conflict with same-conversation intervals.
  Round 8 addresses label ambiguity for some models; Round 9’s sham arms argue
  against directional token priming on the 8-item subset; Round 10 shows that
  the remaining split travels to J&K. It still does not explain every
  Haiku/GPT-4o contradiction.
- Control and treatment differed in conversation length until the Round 7
  matched two-turn control; earlier Round 6 J&K estimates retain that gap.
- The power analysis uses the unfiltered, zero-inflated pilot and a normal
  approximation; it should be revised before a confirmatory run.
- Results generalize only to the tested prompts, models, and snapshots.

## Next iteration

Rounds 7–10 covered the matched two-turn control, stronger anchors, stratified
taxon pilot, clearer comparative labels, matched-distance asymmetry,
sham-token controls, and a confirmatory `TRUE_*` test on J&K. The binder /
non-binder split is the wrap-up claim: it was predicted in a new setting and
held. Token priming is not supported. What remains is narrower than a new
round.

**If anything else is worth doing, it is not load-bearing for this series:**

1. Prefer `TRUE_GREATER` / `TRUE_LESS` for any future comparative-step arm where
   same-turn consistency matters, especially for binder models.
2. Treat contradiction rates as model-specific rather than pooling a single
   protocol diagnosis across providers.
3. Optional desk work: Arm A vs R9 `ready` p50s on the taxon subset.
4. A persist-model test of *why* Haiku fails to bind would be a new evaluation,
   not a missing R10 cell.

The main lesson is that a useful evaluation does not need a positive headline.
This series found a model-heterogeneous contradiction fork that travels off
its discovery subset, a negative result on token priming, limited anchoring
relative to humans, sparse within-model movement that makes means fragile, no
evidence of false confidence, and an aging-stimulus confound.
