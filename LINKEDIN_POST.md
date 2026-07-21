# LinkedIn post draft

Do irrelevant numbers change an LLM's estimate—or how confident it sounds?

This week I built an anchoring-bias evaluation with Inspect AI, adapting the
two-step procedure from Jacowitz and Kahneman:

1. Ask whether the true answer is greater or less than an anchor.
2. Ask for the model's own p10, p50, and p90 estimate.

I ran 15 published questions across Claude Sonnet 4.5, Claude Haiku 4.5,
GPT-4o, and GPT-4o mini: 300 samples and 540 model generations.

The headline result was mostly resistance to anchoring.

- The human median anchoring index reported by J&K was 0.43.
- The model median was 0 in every condition.
- Anchored intervals generally widened slightly rather than becoming falsely
  precise.

The more useful result came from investigating the exceptions.

Some of the original questions are time-sensitive. For example, the 1995
anchors for the number of female professors at Berkeley were 25 and 130, while
one modern model's unanchored estimate was 1,100. That produced a large
anchoring index, but the anchors no longer represented a meaningful low/high
comparison for that model.

Rather than hide the outlier, I kept the complete replication result and added
a sensitivity analysis for cases where the historical anchors still bracketed
the model's baseline. The apparent provenance effect in the raw means
disappeared.

That was the main lesson from this iteration: old behavioral benchmarks can be
valuable protocol bridges without being timeless datasets.

The eval also caught a non-monotonic confidence interval, exposed brittle
exact-string scoring, and helped size a cheaper follow-up using harder
bird-taxonomy questions with model-calibrated anchors.

Next week: strengthen the anchor design, add a protocol-matched control, and run
a staged taxon pilot before testing newer frontier models.

Code, results, and full write-up:
https://github.com/drkalexander1/eval-anchoring-r6

#AI #LLMEvals #AIEngineering
