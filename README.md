# Season 5 — Tactical: The General

**Zhaoqian Xue / purpleman / GitHub @ZhaoqianXue**

## Design goal and submitted policy

Make an army's jobs visible across three capture zones: take unoccupied ground, defend a held zone, and redirect support when local pressure changes. The submitted `agent.Agent` uses the authored policy in `general.py`; the independently trained imitation learner is retained in `learner_agent.py` and `imitation-policy.pt` for comparison.

Each unit begins with a squad preference based on its number within its unit type, distributing footmen, archers, and cavalry among the three zones. On every activation, zone cost combines distance, currently observed friendly/enemy occupancy, and the squad preference. Switching needs a three-point improvement; a sole visible defender stays. Footmen capture or form a shield wall, archers kite, supported cavalry charge, and injured units retreat. Chat reports actual changes in zone/job. No shared commander state or hidden enemy positions are read; a zone with no visible occupants is not known to be empty.

Season 4 ranked sixth on automated results (30.39) and received 4.2/5 from five peers. Feedback found role changes hard to see at army scale. This revision replaces its first-zone focus with three-zone assignment and explicit zone/job reports, while preserving the useful retreat behavior. Its limits include incomplete local knowledge, straight-line threat estimates, and occasional role switching under changing visibility.

**Rating question (1–5):** How clearly did the army spread across capture zones and change between contesting, defending, and retreating as the battle changed?

## Imitation experiment and decision

The official [imitation example](https://github.com/vox-deorum/game-agent-template/tree/examples/skirmish_crane/imitation) supplies the encoder, attention architecture, collector, trainer, and legal-action scoring. The revised three-zone policy supplied **4,118 demonstrations** from seeds 0–5, both seats, versus Naive. Seeds 0–3 supplied 2,422 training rows; 4–5 supplied 1,696 validation rows. All three unit types were included.

Training used CPU, one thread, width 32, one layer, four heads, batch 64, initialization seed 0, and a 45-epoch cap. It took **43.10 seconds**, retained epoch 31, and produced **21,314 parameters**. Validation agreement was **84.73% for tiles**, **99.76% for targets from the teacher's tile**, and **84.55% for complete choices**. These are predictions on recorded states, not wins.

Complete new-seed episodes used seeds **100, 101, 102**, both seats:

| Opponent | Authored teacher mean | Learned mean |
|---|---:|---:|
| Naive | 100.00 | 82.43 |
| Preserved Season 4 policy | 77.60 | 58.46 |

No agent failed or timed out. Against Naive, mean full `act()` time was 0.337 ms (teacher) versus 0.847 ms (learner); maximum observed calls were 24.09 and 38.30 ms. Against Season 4, maxima were 6.84 and 87.70 ms, below the 250 ms decision limit. These are local measurements, not guarantees about server latency. Raw episode and timing records are in `evidence/`.

Against Season 4, the teacher's trace included presence in all three zones across the six matches and 84 changes of job or assigned zone. This does not mean each zone was continuously held. The learner's lower scores and missing explicit commitment memory favor submitting the authored policy. A high agreement rate did not establish strategic reliability.

One inspected disagreement was seed 4, red cavalry 5: the teacher moved offset (3, -2), while the learner chose (1, -1), keeping the same target. The learner's tile was inside a zone but exposed to four immediate visible attackers versus three for the teacher. Agreement can conceal a tradeoff between capture and exposure; this one state does not explain every defeat.

## Reproduce and checks

Use Python 3.12 and the unchanged pinned requirements. `season.json` is the platform's downloaded Season 5 configuration.

```sh
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m sandbox test
python -m imitation.experiment collect --episodes 6 --output runs/reproduced.jsonl
python -m imitation.train runs/reproduced.jsonl --validation-seeds 4 5 --width 32 --layers 1 --heads 4 --epochs 45 --batch-size 64 --threads 1 --device cpu
python -m imitation.experiment evaluate --start 100 --episodes 3 --output runs/reproduced-evaluation.json
python compare.py
python -m sandbox watch --seed 100
```

`compare.py` compares both policies against the preserved Season 4 agent. The experiment helper accepts an optional opponent factory, and its learner entry now explicitly loads `learner_agent.Agent`. `baseline_s4.py` and `s4_blocks.py` preserve the prior implementation. Collection data in `runs/` is ignored; the trained checkpoint and reports are committed. Do not interpret the weak Naive benchmark as peer-competition performance.

## AI use and reflection

This submission was developed with **OpenAI Codex**. Codex read the assignment and feedback, wrote the three-zone policy and comparison tooling, ran collection/training/evaluation, inspected a disagreement, and drafted this README. The official template supplied the underlying environment, tactical blocks, and imitation framework. Validation used project checks, complete held-out episodes on both seats, action-time measurements, and actual behavior traces. No sandbox, manifest, or dependency files were manually changed.

The main lesson was that matching demonstrations is weaker evidence than completing new games. The small learner reproduced many actions, but its independent decisions scored worse and took longer than the rules. The submitted choice follows that measured result. Browser observations and final submission receipts are recorded separately; no claim is made that the student personally operated the tests.
