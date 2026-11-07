"""A stronger held-out comparison against the preserved Season 4 policy, both seats."""
import json
from collections import Counter
from pathlib import Path

from general import Agent as General
from baseline_s4 import Agent as Season4
from imitation.experiment_tools import episode
from sandbox.crane import me, zone


def main():
    results = []
    for seed in (100, 101, 102):
        for seat in (0, 1):
            for kind in ("teacher", "learner"):
                assignments, transitions, presence = Counter(), Counter(), Counter()
                class Tracked(General):
                    def act(self, observation):
                        previous = self.memory.get("report_state")
                        order = super().act(observation)
                        current = self.memory.get("report_state")
                        assignments[str(current)] += 1
                        if previous is not None and current != previous:
                            transitions[f"{previous} -> {current}"] += 1
                        area = zone.at(observation, me.position(observation))
                        if area is not None:
                            presence[str(area["center"])] += 1
                        return order
                row = episode(kind, seed, seat, Tracked, opponent_factory=Season4)
                row.update(opponent="Season4", assignments=dict(assignments),
                           transitions=dict(transitions), zone_presence=dict(presence))
                results.append(row)
                print(json.dumps(row), flush=True)
    Path("evidence").mkdir(exist_ok=True)
    Path("evidence/season4-opponent.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
