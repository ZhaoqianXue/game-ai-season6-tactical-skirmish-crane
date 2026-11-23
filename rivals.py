"""Assign relief to the center while keeping small holds on the wings."""

import blocks
from sandbox.crane import action, me, paths, tile, visible, zone


def contest(observation, memory, goal):
    """Reach or hold the assigned zone, preferring approaches that avoid waste damage."""
    area = zone.at(observation, goal)
    if area is None:
        return None
    view = blocks._View(observation)
    inside = {(spot["q"], spot["r"]) for spot in area["tiles"]}
    holding = (view.position["q"], view.position["r"]) in inside
    terrain = observation["observation"]["battlefield"]["tiles"]
    options = []
    for path in action.legal_paths(observation):
        q, r = view.position["q"], view.position["r"]
        waste = 0
        for direction in paths.decode(path):
            dq, dr = tile.DIRECTIONS[direction]
            q, r = q + dq, r + dr
            waste += terrain[r][q]["feature"] == "waste"
        spot = {"q": q, "r": r}
        victim = blocks._victim(view, spot)
        on_zone = (q, r) in inside
        # Standing in waste is free. Count every entry along the route, not only its end.
        cost = 2 * tile.distance(spot, goal) + 5 * waste - 3 * (victim is not None)
        score = (holding and not on_zone, cost - 3 * on_zone, waste, path)
        options.append((score, path, victim))
    _, path, victim = min(options, key=lambda candidate: candidate[0])
    return blocks._order(view, path, victim)


def assignment(observation, memory):
    areas = sorted(zone.zones(observation), key=lambda area: (area["center"]["r"], area["center"]["q"]))
    if len(areas) < 3:
        return blocks.assign(observation, memory)

    here = me.position(observation)
    side = me.side(observation)
    kind = me.unit_type(observation)
    number = int(me.unit_id(observation).rsplit("_", 1)[1])
    foes = visible.enemies(observation)
    friends = visible.allies(observation)
    middle = min(range(len(areas)), key=lambda i: tile.distance(areas[i]["center"], tile.at_center(observation)))
    home = number % len(areas)
    friendly_inside = []
    hostile_inside = []
    for area in areas:
        occupants = zone.occupants(observation, area)
        friendly_inside.append(sum(unit["side"] == side for unit in occupants))
        hostile_inside.append(sum(unit["side"] != side for unit in occupants))

    middle_pressure = sum(tile.distance(unit["position"], areas[middle]["center"]) <= 3 for unit in foes)

    def priority(index):
        # Give the middle a limited relief preference when opponents are visible there.
        # The last wing defender keeps its zone even if reinforcements are called.
        calls_for_relief = index == middle and middle_pressure > friendly_inside[middle] and number % 3 != 0
        surplus = max(0, friendly_inside[index] - 1) if index != middle and not hostile_inside[index] else 0
        return (
            tile.distance(here, areas[index]["center"])
            + (0 if index == home else 4)
            + 3 * friendly_inside[index]
            + 2 * surplus
            - 3 * min(hostile_inside[index], 2)
            - (4 if calls_for_relief else 0)
        )

    current = memory.get("zone", home)
    if current >= len(areas):
        current = home
    holding = zone.at(observation, here)
    guard = holding == areas[current] and friendly_inside[current] == 1
    challenger = min(range(len(areas)), key=priority)
    if not guard and priority(challenger) + 3 < priority(current):
        current = challenger
    memory["zone"] = current
    heart = areas[current]["center"]
    local_foes = [unit for unit in foes if tile.distance(unit["position"], heart) <= 4]
    threatened = any(tile.distance(here, unit["position"]) <= 2 for unit in foes)
    exposed_to_cavalry = any(
        unit["type"] == "cavalry" and tile.distance(here, unit["position"]) <= 4 for unit in foes
    )
    if kind == "archer":
        if threatened and me.hit_points(observation) <= 2 and not guard:
            return blocks.fall_back, heart
        if foes and (exposed_to_cavalry or not guard):
            return blocks.kite, heart
        # Stay on a paying zone when this archer is the sole holder and there is no charge threat.
        return contest, heart
    if kind == "footman":
        return (blocks.shield_wall if local_foes and number % 2 and not guard
                else contest), heart
    if foes and me.hit_points(observation) <= 3 and not guard:
        return blocks.fall_back, heart
    support = any(tile.distance(here, unit["position"]) <= 4 for unit in friends)
    if local_foes and support and friendly_inside[current] and not guard:
        return blocks.charge, heart
    if friendly_inside[current] and not guard and not local_foes:
        return blocks.hold_ground, heart
    return contest, heart


class Agent:
    def __init__(self):
        self.memory = {}

    def reset(self, seed, observation):
        self.memory.clear()

    def act(self, observation):
        job, goal = assignment(observation, self.memory)
        state = (self.memory.get("zone", 0), job.__name__)
        if state != self.memory.get("last_report"):
            self.memory["last_report"] = state
            self.memory["report"] = f"Zone {state[0] + 1}: {state[1]}."
        return job(observation, self.memory, goal) or contest(
            observation, self.memory, goal
        ) or blocks.advance(observation, self.memory, goal)

    def chat(self, inbox):
        report = self.memory.pop("report", None)
        return [] if report is None else [{"to": None, "text": report}]
