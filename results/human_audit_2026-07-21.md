# Human translation audit

Selection seed: `20260721`  
Random audit records: **20**  
Mandatory parser exceptions: **1**

Review every checkbox against the raw transcript. Do not mark the audit
complete until all 20 sampled records and all mandatory exceptions have
a named reviewer, timestamp, verdict, and any discrepancy notes.

# Stratified random sample

## A01 — R6 J&K — Claude Sonnet 4.5

- Item: `jk_meat_per_year`
- Condition: `control`
- Anchor: `None`
- Source sample: `jk_meat_per_year::control::s0`
- Scorer result: **180.0 / 220.0 / 260.0**
- Fresh reparse from raw output: `[180.0, 220.0, 260.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
Answer the following question with an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

Question: How many pounds of meat does the average American eat per year?

```
**ASSISTANT**
```text
180 220 260
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A02 — R6 J&K — Claude Haiku 4.5

- Item: `jk_berkeley_female_professors`
- Condition: `control`
- Anchor: `None`
- Source sample: `jk_berkeley_female_professors::control::s0`
- Scorer result: **320.0 / 420.0 / 520.0**
- Fresh reparse from raw output: `[320.0, 420.0, 520.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
Answer the following question with an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

Question: How many female professors are there at the University of California, Berkeley?

```
**ASSISTANT**
```text
320 420 520
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A03 — R6 J&K — GPT-4o

- Item: `jk_everest_height`
- Condition: `low_arb`
- Anchor: `2000.0`
- Source sample: `jk_everest_height::low_arb::s0`
- Scorer result: **28700.0 / 29029.0 / 29200.0**
- Fresh reparse from raw output: `[28700.0, 29029.0, 29200.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
A random number generator just produced the number 2000.

Question: What is the height of Mount Everest, in feet?

Is the true answer greater or less than 2000?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
Greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
28700 29029 29200
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A04 — R6 J&K — GPT-4o mini

- Item: `jk_sf_nyc_distance`
- Condition: `low_arb`
- Anchor: `1500.0`
- Source sample: `jk_sf_nyc_distance::low_arb::s0`
- Scorer result: **250.0 / 2800.0 / 3200.0**
- Fresh reparse from raw output: `[250.0, 2800.0, 3200.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
A random number generator just produced the number 1500.

Question: What is the distance from San Francisco to New York City, in miles?

Is the true answer greater or less than 1500?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
less
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
250  2800  3200
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A05 — R6 J&K — Claude Sonnet 4.5

- Item: `jk_un_members`
- Condition: `high_arb`
- Anchor: `127.0`
- Source sample: `jk_un_members::high_arb::s0`
- Scorer result: **190.0 / 193.0 / 195.0**
- Fresh reparse from raw output: `[190.0, 193.0, 195.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
A random number generator just produced the number 127.

Question: How many member countries does the United Nations have?

Is the true answer greater or less than 127?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
190 193 195
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A06 — R6 J&K — GPT-4o

- Item: `jk_tallest_redwood`
- Condition: `high_arb`
- Anchor: `550.0`
- Source sample: `jk_tallest_redwood::high_arb::s0`
- Scorer result: **310.0 / 360.0 / 380.0**
- Fresh reparse from raw output: `[310.0, 360.0, 380.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
A random number generator just produced the number 550.

Question: What is the height of the tallest redwood tree, in feet?

Is the true answer greater or less than 550?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
Greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
310 360 380
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A07 — R6 J&K — Claude Haiku 4.5

- Item: `jk_everest_height`
- Condition: `low_plaus`
- Anchor: `2000.0`
- Source sample: `jk_everest_height::low_plaus::s0`
- Scorer result: **28500.0 / 29032.0 / 29500.0**
- Fresh reparse from raw output: `[28500.0, 29032.0, 29500.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
An analyst estimated that the answer to the following question is about 2000.

Question: What is the height of Mount Everest, in feet?

Is the true answer greater or less than 2000?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
28500 29032 29500
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A08 — R6 J&K — GPT-4o mini

- Item: `jk_everest_height`
- Condition: `low_plaus`
- Anchor: `2000.0`
- Source sample: `jk_everest_height::low_plaus::s0`
- Scorer result: **2500.0 / 29029.0 / 30000.0**
- Fresh reparse from raw output: `[2500.0, 29029.0, 30000.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
An analyst estimated that the answer to the following question is about 2000.

Question: What is the height of Mount Everest, in feet?

Is the true answer greater or less than 2000?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
2500  29029  30000
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A09 — R6 J&K — Claude Sonnet 4.5

- Item: `jk_cat_speed`
- Condition: `high_plaus`
- Anchor: `30.0`
- Source sample: `jk_cat_speed::high_plaus::s0`
- Scorer result: **25.0 / 30.0 / 35.0**
- Fresh reparse from raw output: `[25.0, 30.0, 35.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
An analyst estimated that the answer to the following question is about 30.

Question: What is the maximum speed of a house cat, in miles per hour?

Is the true answer greater or less than 30?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
less
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
25 30 35
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A10 — R6 J&K — GPT-4o mini

- Item: `jk_telephone_year`
- Condition: `high_plaus`
- Anchor: `1920.0`
- Source sample: `jk_telephone_year::high_plaus::s0`
- Scorer result: **1845.0 / 1876.0 / 1890.0**
- Fresh reparse from raw output: `[1845.0, 1876.0, 1890.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
An analyst estimated that the answer to the following question is about 1920.

Question: In what year was the telephone invented?

Is the true answer greater or less than 1920?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
less
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
1845  1876  1890
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A11 — R7 taxon — Claude Haiku 4.5

- Item: `order_falconiformes`
- Condition: `control`
- Anchor: `None`
- Source sample: `order_falconiformes::control::s0`
- Scorer result: **60.0 / 75.0 / 95.0**
- Fresh reparse from raw output: `[60.0, 75.0, 95.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
You will estimate the answer to the following question in the next turn.

Question: How many bird species are currently recognized in the order Falconiformes worldwide?

Respond with exactly one word: "ready".

```
**ASSISTANT**
```text
ready
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
60 75 95
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A12 — R7 taxon — GPT-4o

- Item: `anas_anatidae_genus`
- Condition: `control`
- Anchor: `None`
- Source sample: `anas_anatidae_genus::control::s0`
- Scorer result: **25.0 / 30.0 / 35.0**
- Fresh reparse from raw output: `[25.0, 30.0, 35.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
You will estimate the answer to the following question in the next turn.

Question: How many bird species are currently recognized in the genus Anas worldwide?

Respond with exactly one word: "ready".

```
**ASSISTANT**
```text
Ready.
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
25 30 35
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A13 — R7 taxon — GPT-4o mini

- Item: `family_alcidae`
- Condition: `low_arb`
- Anchor: `16.0`
- Source sample: `family_alcidae::low_arb::s0`
- Scorer result: **10.0 / 22.0 / 30.0**
- Fresh reparse from raw output: `[10.0, 22.0, 30.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
A random number generator just produced the number 16.

Question: How many bird species are currently recognized in the family Alcidae worldwide?

Is the true answer greater or less than 16?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
10  22  30
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A14 — R7 taxon — Claude Sonnet 4.5

- Item: `order_falconiformes`
- Condition: `low_arb`
- Anchor: `53.0`
- Source sample: `order_falconiformes::low_arb::s0`
- Scorer result: **300.0 / 350.0 / 420.0**
- Fresh reparse from raw output: `[300.0, 350.0, 420.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
A random number generator just produced the number 53.

Question: How many bird species are currently recognized in the order Falconiformes worldwide?

Is the true answer greater or less than 53?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
300 350 420
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A15 — R7 taxon — Claude Haiku 4.5

- Item: `eudyptula_spheniscidae_genus`
- Condition: `high_arb`
- Anchor: `4.0`
- Source sample: `eudyptula_spheniscidae_genus::high_arb::s0`
- Scorer result: **1.0 / 2.0 / 3.0**
- Fresh reparse from raw output: `[1.0, 2.0, 3.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
A random number generator just produced the number 4.

Question: How many bird species are currently recognized in the genus Eudyptula worldwide?

Is the true answer greater or less than 4?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
1 2 3
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A16 — R7 taxon — GPT-4o mini

- Item: `falco_falconidae_genus`
- Condition: `high_arb`
- Anchor: `50.0`
- Source sample: `falco_falconidae_genus::high_arb::s0`
- Scorer result: **35.0 / 40.0 / 45.0**
- Fresh reparse from raw output: `[35.0, 40.0, 45.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
A random number generator just produced the number 50.

Question: How many bird species are currently recognized in the genus Falco worldwide?

Is the true answer greater or less than 50?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
35  40  45
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A17 — R7 taxon — GPT-4o

- Item: `family_anatidae`
- Condition: `low_plaus`
- Anchor: `130.0`
- Source sample: `family_anatidae::low_plaus::s0`
- Scorer result: **145.0 / 160.0 / 175.0**
- Fresh reparse from raw output: `[145.0, 160.0, 175.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
An analyst estimated that the answer to the following question is about 130.

Question: How many bird species are currently recognized in the family Anatidae worldwide?

Is the true answer greater or less than 130?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
Greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
145 160 175
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A18 — R7 taxon — Claude Sonnet 4.5

- Item: `order_accipitriformes`
- Condition: `low_plaus`
- Anchor: `215.0`
- Source sample: `order_accipitriformes::low_plaus::s0`
- Scorer result: **240.0 / 265.0 / 290.0**
- Fresh reparse from raw output: `[240.0, 265.0, 290.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
An analyst estimated that the answer to the following question is about 215.

Question: How many bird species are currently recognized in the order Accipitriformes worldwide?

Is the true answer greater or less than 215?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
240 265 290
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A19 — R7 taxon — Claude Haiku 4.5

- Item: `corvus_corvidae_genus`
- Condition: `high_plaus`
- Anchor: `59.0`
- Source sample: `corvus_corvidae_genus::high_plaus::s0`
- Scorer result: **45.0 / 50.0 / 55.0**
- Fresh reparse from raw output: `[45.0, 50.0, 55.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
An analyst estimated that the answer to the following question is about 59.

Question: How many bird species are currently recognized in the genus Corvus worldwide?

Is the true answer greater or less than 59?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
greater
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
45 50 55
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

## A20 — R7 taxon — GPT-4o

- Item: `ramphastos_ramphastidae_genus`
- Condition: `high_plaus`
- Anchor: `11.0`
- Source sample: `ramphastos_ramphastidae_genus::high_plaus::s0`
- Scorer result: **6.0 / 8.0 / 10.0**
- Fresh reparse from raw output: `[6.0, 8.0, 10.0]`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
An analyst estimated that the answer to the following question is about 11.

Question: How many bird species are currently recognized in the genus Ramphastos worldwide?

Is the true answer greater or less than 11?
Respond with exactly one word: "greater" or "less".

```
**ASSISTANT**
```text
Less
```
**USER**
```text
Now give your own answer to that question as an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

```
**ASSISTANT**
```text
6 8 10
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:

# Mandatory exception review

These records failed automatic parsing and are reviewed in addition
to the 20-record random sample.

## E01 — R6 J&K — GPT-4o mini

- Item: `jk_cat_speed`
- Condition: `control`
- Anchor: `None`
- Source sample: `jk_cat_speed::control::s0`
- Scorer result: **REJECTED**
- Fresh reparse from raw output: `None`
- Stored score matches fresh reparse: `True`

### Raw transcript

**USER**
```text
Answer the following question with an 80% central interval (p10, p50, p90).

Respond with EXACTLY three numbers on one line, whitespace-separated, in this order:
p10  p50  p90

No units, no prose, no labels.

Question: What is the maximum speed of a house cat, in miles per hour?

```
**ASSISTANT**
```text
30  25  35
```

### Human verification

- [ ] Raw response matches the source transcript
- [ ] Parsed p10/p50/p90 values are correct
- [ ] Condition, anchor, and provenance match the prompt
- [ ] First-turn response or control acknowledgement is recorded correctly
- Verdict: `pending`
- Reviewer:
- Reviewed at:
- Notes:
