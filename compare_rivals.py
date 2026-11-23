"""Play paired, full games on both seats against a pusher and a zone holder."""

import argparse
import json
from collections import Counter
from pathlib import Path

import blocks
from baseline_s4 import Agent as Pusher
from general import Agent as General
from imitation.experiment_tools import action_labels, episode
from rivals import Agent as Rivals
from sandbox.crane import me, tile, zone


class CenterHold:
    """A static opponent that advances to the middle and stays inside while attacking."""

    def reset(self, seed, observation):
        self.memory = {}

    def act(self, observation):
        board_center = tile.at_center(observation)
        middle = min(zone.zones(observation), key=lambda area: tile.distance(area["center"], board_center))
        return blocks.capture(observation, self.memory, middle["center"])


def compare(policy, opponent, seed, seat):
    positions = Counter()
    decisions = Counter()

    class Tracked(policy):
        def act(self, observation):
            order = super().act(observation)
            action_labels(observation, order)
            board_center = tile.at_center(observation)
            middle = min(zone.zones(observation), key=lambda area: tile.distance(area["center"], board_center))
            if zone.at(observation, me.position(observation)) == middle:
                positions["in_middle"] += 1
            positions["total"] += 1
            report = self.memory.get("last_report", self.memory.get("report_state"))
            if report is not None:
                decisions[report[1]] += 1
            return order

    result = episode("teacher", seed, seat, Tracked, opponent_factory=opponent)
    return dict(result, agent=policy.__module__, opponent=opponent.__name__,
                center_share=positions["in_middle"] / max(1, positions["total"]),
                decisions=dict(decisions))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[103, 104, 105])
    parser.add_argument("--output", type=Path, default=Path("evidence/rivals-comparison.json"))
    args = parser.parse_args()
    results = []
    for opponent in (Pusher, CenterHold):
        for seed in args.seeds:
            for seat in (0, 1):
                for policy in (General, Rivals):
                    result = compare(policy, opponent, seed, seat)
                    results.append(result)
                    print(f"{policy.__module__:7} vs {opponent.__module__:12} seed={seed} seat={seat}"
                          f" score={result['score']:.2f} center={result['center_share']:.1%}"
                          f" reason={result['reason']} timeouts={result['own_timeouts']}", flush=True)
    args.output.parent.mkdir(exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
