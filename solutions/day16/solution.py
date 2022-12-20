import re

from sortedcontainers import SortedList

from .models import DoublePath, Network, Path, Valve

LINE_REGEX = (
    r"Valve (?P<name>\w\w) has flow rate=(?P<rate>\d+); "
    r"tunnels? leads? to valves? (?P<connections>\w\w(?:, \w\w)*)"
)


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    connections: list[tuple[str, str]] = []
    valves_by_name: dict[str, Valve] = {}
    for line in inputs:
        valve, line_connections = parse_line(line)
        connections.extend((valve.name, conn) for conn in line_connections)
        valves_by_name[valve.name] = valve
    network = Network(valves_by_name, connections)
    starting_valve = valves_by_name["AA"]

    paths = SortedList(
        [
            Path(
                network=network,
                valves_opened={},
                minute=1,
                location=starting_valve,
                current_travel=set(),
            )
        ],
        key=lambda p: p.maximum_value,
    )
    best_complete_path: Path | None = None
    count = 0
    max_paths_length = 0
    if debug:
        network_distances = len(network._dist_cache)
    while paths:
        count += 1
        max_paths_length = max(max_paths_length, len(paths))
        best_incomplete_path: Path = paths.pop()
        if best_complete_path is not None:
            if best_incomplete_path.maximum_value < best_complete_path.current_value:
                break

        new_paths = best_incomplete_path.next_iterations()
        for path in new_paths:
            if path.complete:
                if best_complete_path is None:
                    best_complete_path = path
                elif best_complete_path.current_value < path.current_value:
                    best_complete_path = path
            else:
                paths.add(path)
        if debug:
            new = len(network._dist_cache) - network_distances
            if new > 0:
                # print(f"Calculated {new} distances (total {new + network_distances})")
                network_distances += new
    debug and print(f"Tried {count} path steps")
    debug and print(f"Candidates paths was at most {max_paths_length}")
    assert best_complete_path is not None
    part1 = best_complete_path.current_value
    debug and print("=" * 30)

    double_paths = SortedList(
        [
            DoublePath(
                network=network,
                valves_opened={},
                minute=1,
                location=(starting_valve, starting_valve),
                current_travel=(set(), set()),
            )
        ],
        key=lambda p: p.maximum_value,
    )
    best_complete_double_path: DoublePath | None = None
    count = 0
    max_paths_length = 0
    while double_paths:
        count += 1
        if debug and (count % 1000 == 0):
            print(f"Path step {count}")
            print(f"Best maximum: {double_paths[-1].maximum_value}")
        max_paths_length = max(max_paths_length, len(double_paths))
        best_incomplete_double_path: DoublePath = double_paths.pop()
        if best_complete_double_path is not None:
            if (
                best_incomplete_double_path.maximum_value
                < best_complete_double_path.current_value
            ):
                break

        new_double_paths = best_incomplete_double_path.next_iterations()
        for double_path in new_double_paths:
            if double_path.complete:
                if (
                    best_complete_double_path is None
                    or best_complete_double_path.current_value < path.current_value
                ):
                    best_complete_double_path = double_path
                    debug and print(
                        f"New best: {best_complete_double_path.current_value}"
                    )
            elif (
                not double_paths
                or double_paths[-1].current_value <= double_path.maximum_value
            ):
                double_paths.add(double_path)
        if debug:
            new = len(network._dist_cache) - network_distances
            if new > 0:
                # print(f"Calculated {new} distances (total {new + network_distances})")
                network_distances += new
    debug and print(f"Tried {count} path steps")
    debug and print(f"Candidates paths was at most {max_paths_length}")
    assert best_complete_double_path is not None
    # debug and print(best_complete_double_path.valves_opened)
    part2 = best_complete_double_path.current_value
    debug and print("=" * 30)

    return part1, part2


def parse_line(line: str) -> tuple[Valve, list[str]]:
    match = re.match(LINE_REGEX, line)
    assert match, line
    name, rate, connections = match.groups()
    return Valve(name, int(rate)), connections.split(", ")
