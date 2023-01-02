import re

from sortedcontainers import SortedList

from .models import Blueprint, FactoryState, Resource, ResourceSet

BLUEPRINT_PATTERN = (
    r"Blueprint (\d+): Each ore robot costs (\d+) ore. "
    r"Each clay robot costs (\d+) ore. "
    r"Each obsidian robot costs (\d+) ore and (\d+) clay. "
    r"Each geode robot costs (\d+) ore and (\d+) obsidian."
)
PART_ONE_TIME_LIMIT = 24
PART_TWO_TIME_LIMIT = 32


def alpha(inputs: list[str], debug: bool = False) -> tuple[int, int]:
    initial_factory_states = list(map(build_initial_state, inputs))

    quality = 0
    for initial_state in initial_factory_states:
        max_geodes = maximize_geodes(initial_state, PART_ONE_TIME_LIMIT, debug)
        quality += initial_state.blueprint.number * max_geodes
    part1 = quality

    product = 1
    for initial_state in initial_factory_states[:3]:
        max_geodes = maximize_geodes(initial_state, PART_TWO_TIME_LIMIT, debug)
        product *= max_geodes
    part2 = product

    return part1, part2


def build_initial_state(input_line: str) -> FactoryState:
    blueprint = parse_blueprint(input_line)
    return FactoryState(blueprint, ResourceSet(), ResourceSet(ore=1))


def parse_blueprint(input_line: str) -> Blueprint:
    match = re.match(BLUEPRINT_PATTERN, input_line)
    assert match is not None
    values = list(map(int, match.groups()))
    blueprint = Blueprint(
        values[0],
        ResourceSet(ore=values[1]),
        ResourceSet(ore=values[2]),
        ResourceSet(ore=values[3], clay=values[4]),
        ResourceSet(ore=values[5], obsidian=values[6]),
    )
    return blueprint


def maximize_geodes(initial_state: FactoryState, time_limit: int, debug: bool) -> int:
    frontier = SortedList([(initial_state, time_limit)], key=sort_key)
    best_state: FactoryState | None = None
    ticker = 0
    while len(frontier) > 0:
        candidate_time: tuple[FactoryState, int] = frontier.pop()
        candidate, time_left = candidate_time
        if time_left <= 0:
            if (
                best_state is None
                or best_state.resources.geode < candidate.resources.geode
            ):
                best_state = candidate
        else:
            if (
                best_state is not None
                and best_state.resources.geode >= candidate.heuristic(time_left)
            ):
                break
            frontier.update(candidate.branch(time_left))
        ticker += 1
        debug and ticker % 1000 == 0 and print(
            ticker, len(frontier), best_state and best_state.resources
        )
    assert best_state is not None
    return best_state.resources.geode


def sort_key(state_time: tuple[FactoryState, int]) -> int:
    state, time_left = state_time
    return state.heuristic(time_left)
