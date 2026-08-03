# R8 write-up number audit

Checked against Inspect `.eval` logs and `scripts/analyze_contradiction.py`
(whole-interval contradictions on `data/contradiction_subset_r8.yaml`).

Percentages in the write-up are rounded (e.g. 12/32 = 37.5% → 38%).

## Ambiguous-label column

| Model | Source | Count | Write-up |
|---|---|---|---|
| Haiku 4.5 | Round 7 taxon pilot → 8-item filter | 12/32 | 12/32 (38%) |
| GPT-4o mini | Round 7 taxon pilot → 8-item filter | 4/32 | 4/32 (12%) |
| Sonnet 4.5 | Round 7 taxon pilot → 8-item filter | 12/32 | 12/32 (38%) |
| GPT-4o | Round 7 taxon pilot → 8-item filter | 12/32 | 12/32 (38%) |
| Sonnet 5 | R8 rerun `greater_less` + outside | 7/32 | 7/32 (22%) |
| Opus 4.5 | R8 rerun `greater_less` + outside | 1/32 | 1/32 (3%) |

## Arm A (`TRUE_*` + outside)

| Model | Log-derived | Write-up |
|---|---|---|
| Haiku 4.5 | 11/32 | 11/32 (34%) |
| GPT-4o mini | 2/32 | 2/32 (6%) |
| Sonnet 4.5 | 0/32 | 0/32 (0%) |
| GPT-4o | 10/32 | 10/32 (31%) |
| Sonnet 5 | 5/30 | 5/30 (17%) |
| Opus 4.5 | 0/32 | 0/32 (0%) |

## Arm B (`greater_less` + matched_distance)

| Model | Log-derived | Write-up |
|---|---|---|
| Haiku 4.5 | 10/32 | 10/32 (31%) |
| GPT-4o mini | 3/32 | 3/32 (9%) |
| Sonnet 4.5 | 12/32 | 12/32 (38%) |
| GPT-4o | 13/32 | 13/32 (41%) |

## Notes for manual pass

- Sonnet 5 Arm A parse mean was 0.950 (38/40 samples); anchored parsed n=30.
- Ambiguous-label sources differ by model family as noted above; both use the
  same 8 items, outside anchors, strength 2, matched control.
- Result JSON mirrors: `results/r8_*.json`,
  `results/r8_r7style_sonnet5_opus45.json`.
