import re

from sortedcontainers import SortedList

from .models import Path, Valve

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

    part2 = 0
    return part1, part2


def parse_line(line: str) -> tuple[Valve, list[str]]:
    match = re.match(LINE_REGEX, line)
    assert match, line
    name, rate, connections = match.groups()
    return Valve(name, int(rate)), connections.split(", ")
