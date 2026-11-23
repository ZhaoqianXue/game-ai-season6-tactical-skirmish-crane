# Season 6 — Tactical: The Rivals

Zhaoqian Xue / purpleman / GitHub @ZhaoqianXue

## Design goal

Use spare units to reinforce the middle when it comes under pressure, while a small guard keeps scoring on quieter ground. Archers can still kite a nearby threat, and routine moves avoid wasting hit points on hazardous tiles when a comparable route is available.

**Rating question (1–5):** When opponents contest the middle, how clearly does the army redirect spare units there while keeping a defender on quieter ground?

## Changes after Season 5

The Season 5 agent averaged 36.56 on the platform's automated board and 3.2/5 from five peers. Several reviewers saw troops accumulate in the back zone while the center went to the opponent. The new policy preserves the original squad preferences but makes a visible friendly surplus on a quiet wing a reason to move. The middle gets a relief bonus when visible opponents near it outnumber friendly holders. The last visible defender keeps its assignment. Every unit decides from its own observations, so units can disagree about which zone needs help.

An archer which is the last holder can stay inside the zone when it sees no nearby cavalry. Under close pressure, injured units with a replacement can retreat. Normal capture movement prices the hit-point cost of entering wasteland on each step. In the first trial, weighting the center more heavily increased its occupancy but hurt scoring against a static holder. The limited version leaves more troops available to score elsewhere.

The Class 12 material motivated practice against opponents that expose different weaknesses. I considered training from the final team score and retaining the Season 5 imitation policy. The submitted entry point uses authored rules, so it needs no new training or weights. The old General and learner remain available for reproduction.

## Verification

`season.json` is the platform download for The Rivals. It enables the army, three capture zones, terrain, wasteland, and unit abilities on an extent-12 field. Development comparisons used seeds 100–101. Final comparisons used the same three new seeds (103–105) and both seats for both policies against each frozen opponent. Each cell is the mean of six complete games.

| Opponent | Season 5 score | Season 6 score | Season 5 center presence | Season 6 center presence |
| --- | ---: | ---: | ---: | ---: |
| Season 4 pusher | 75.30 | 85.17 | 0.46% | 0.93% |
| Static center holder | 92.72 | 100.00 | 4.03% | 7.08% |

Center presence is the proportion of this army's unit activations that started inside the middle zone. It does not measure control of the zone or continuous occupancy. The center pusher still beat the revised policy on some maps, including seed 104, seat 1, where the score dropped from 100.00 to 70.00. Across all 24 evaluation games, no unit timed out or failed. The largest measured full activation for the revised tracked policy was 19.50 ms. This local benchmark does not predict leaderboard placement.

Run `python -m sandbox test` and `python compare_rivals.py` in Python 3.12 with the provided requirements. All **156** project checks passed. Detailed per-match scores, decisions, and timings are in `evidence/rivals-comparison.json`.

## AI use and reflection

OpenAI Codex inspected the course brief and Season 5 feedback, wrote the zone and route changes and the comparison driver, ran the checks and simulations, and drafted this README. The course template provides the environment and legal-action helpers. The matchup comparison caught a regression that a completion test would miss. Using a held-out seed set and checking both seats made the tradeoff visible. These results describe local tests operated by Codex.
