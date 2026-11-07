"""Three-zone squads with local relief decisions; no shared or hidden unit state."""

import blocks
from sandbox.crane import me, tile, visible, zone


def assignment(observation, memory):
    areas = sorted(zone.zones(observation), key=lambda z: (z["center"]["r"], z["center"]["q"]))
    if not areas:
        return blocks.assign(observation, memory)
    here, side = me.position(observation), me.side(observation)
    number = int(me.unit_id(observation).rsplit("_", 1)[1])
    home = number % len(areas)
    enemies, allies = visible.enemies(observation), visible.allies(observation)

    def cost(index):
        area = areas[index]
        occupants = zone.occupants(observation, area)
        friends = sum(u["side"] == side for u in occupants)
        foes = sum(u["side"] != side for u in occupants)
        return (tile.distance(here, area["center"]) + 3 * friends - 3 * min(foes, 2)
                + (0 if index == home else 4))

    current = memory.get("zone", home)
    challenger = min(range(len(areas)), key=cost)
    holding = zone.at(observation, here)
    sole_defender = holding == areas[current] and sum(
        u["side"] == side for u in zone.occupants(observation, areas[current])
    ) == 1
    if not sole_defender and cost(challenger) + 3 < cost(current):
        current = challenger
    memory["zone"] = current
    heart = areas[current]["center"]
    kind = me.unit_type(observation)
    near = [u for u in enemies if tile.distance(u["position"], heart) <= 4]
    if kind == "archer":
        if me.hit_points(observation) <= 2 and any(tile.distance(here, u["position"]) <= 2 for u in enemies):
            return blocks.fall_back, heart
        return blocks.kite, heart
    if kind == "footman":
        return (blocks.shield_wall if near and number % 2 else blocks.capture), heart
    if me.hit_points(observation) <= 3 and enemies:
        return blocks.fall_back, heart
    occupants = zone.occupants(observation, areas[current])
    if not any(u["side"] == side for u in occupants):
        return blocks.capture, heart
    supported = any(tile.distance(here, u["position"]) <= 4 for u in allies)
    return (blocks.charge if near and supported else blocks.hold_ground), heart


class Agent:
    def __init__(self):
        self.memory = {}

    def reset(self, seed, observation):
        self.memory = {}

    def act(self, observation):
        job, goal = assignment(observation, self.memory)
        report = (self.memory.get("zone", 0), job.__name__)
        if report != self.memory.get("report_state"):
            self.memory["report_state"] = report
            self.memory["report"] = f"Zone {report[0] + 1}: {report[1]}."
        return job(observation, self.memory, goal) or blocks.advance(observation, self.memory, goal)

    def chat(self, inbox):
        report = self.memory.pop("report", None)
        return [] if report is None else [{"to": None, "text": report}]
