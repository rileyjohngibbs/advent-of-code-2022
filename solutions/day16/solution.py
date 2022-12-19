import re

from sortedcontainers import SortedList

from .models import DoublePath, Path, Valve

LINE_REGEX = (
    r"Valve (?P<name>\w\w) has flow rate=(?P<rate>\d+); "
    r"tunnels? leads? to valves? (?P<connections>\w\w(?:, \w\w)*)"
)


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    network: dict[Valve, list[Valve]] = {}
    connections: list[tuple[str, str]] = []
    valves_by_name: dict[str, Valve] = {}
    for line in inputs:
        valve, line_connections = parse_line(line)
        connections.extend((valve.name, conn) for conn in line_connections)
        network[valve] = []
        valves_by_name[valve.name] = valve
    for start, end in connections:
        network[valves_by_name[start]].append(valves_by_name[end])
    starting_valve = next(v for v in network if v.name == "AA")

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
    debug and print(f"Tried {count} path steps")
    debug and print(f"Candidates paths was at most {max_paths_length}")
    assert best_complete_path is not None
    part1 = best_complete_path.current_value

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
    # max_paths_length = 0
    while double_paths:
        count += 1
        # max_paths_length = max(max_paths_length, len(double_paths))
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
                if best_complete_double_path is None:
                    best_complete_double_path = double_path
                    debug and print(
                        f"New best: {best_complete_double_path.current_value}"
                    )
                elif best_complete_double_path.current_value < path.current_value:
                    best_complete_double_path = double_path
                    debug and print(
                        f"New best: {best_complete_double_path.current_value}"
                    )
            else:
                double_paths.add(double_path)
    debug and print(f"Tried {count} path steps")
    # debug and print(f"Candidates paths was at most {max_paths_length}")
    assert best_complete_double_path is not None
    # debug and print(best_complete_double_path.valves_opened)
    part2 = best_complete_double_path.current_value

    return part1, part2


def parse_line(line: str) -> tuple[Valve, list[str]]:
    match = re.match(LINE_REGEX, line)
    assert match, line
    name, rate, connections = match.groups()
    return Valve(name, int(rate)), connections.split(", ")
