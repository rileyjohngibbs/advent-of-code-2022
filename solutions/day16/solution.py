import re

from sortedcontainers import SortedList

from .models import TIMERS, DoublePath, Network, Path, Valve

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
    part1 = part_one_alpha(network=network, starting_valve=starting_valve, debug=debug)
    print("=" * 30)
    part2 = part_two_alpha(network=network, starting_valve=starting_valve, debug=debug)
    print("=" * 30)
    return part1, part2


def part_one_alpha(network: Network, starting_valve: Valve, debug: bool) -> int:
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
    return best_complete_path.current_value


def part_two_alpha(network: Network, starting_valve: Valve, debug: bool) -> int:
    try:
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
        """
        If path A and path B have the same valves opened
        and path A and path B have the same location
        and path A's minute is at least path B's minute
        and path A's current value is less than path B's
        then path A cannot beat path B and should be discarded
        """
        # opened, location
        visited: dict[tuple[frozenset[Valve], frozenset[Valve]], list[DoublePath]] = {
            visited_key(double_paths[0]): [double_paths[0]]
        }
        while double_paths:
            count += 1
            if debug and (count % 1000 == 0):
                print(f"Path step {count}")
                print(f"Best maximum: {double_paths[-1].maximum_value}")
                print(f"Paths remaining: {len(double_paths)}")
            max_paths_length = max(max_paths_length, len(double_paths))
            best_incomplete_double_path: DoublePath | None = None
            while best_incomplete_double_path is None:
                best_incomplete_double_path = double_paths.pop()
                cand_key = visited_key(best_incomplete_double_path)
                if best_incomplete_double_path not in visited[cand_key]:
                    best_incomplete_double_path = None
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
                        or best_complete_double_path.current_value
                        < double_path.current_value
                    ):
                        best_complete_double_path = double_path
                        debug and print(
                            f"New best: {best_complete_double_path.current_value}"
                        )
                else:
                    baseline: int
                    if best_complete_double_path is not None:
                        baseline = best_complete_double_path.current_value
                    elif len(double_paths) > 0:
                        baseline = double_paths[-1].current_value
                    else:
                        baseline = 0
                    if double_path.maximum_value > baseline:
                        key = visited_key(double_path)
                        if key not in visited:
                            visited[key] = [double_path]
                            double_paths.add(double_path)
                        elif not any(
                            vp.minute <= double_path.minute
                            and double_path.current_value <= vp.current_value
                            for vp in visited[key]
                        ):
                            visited[key] = [
                                vp
                                for vp in visited[key]
                                if double_path.minute <= vp.minute
                                and vp.current_value <= double_path.current_value
                            ]
                            visited[key].append(double_path)
                            double_paths.add(double_path)
        debug and print(f"Tried {count} path steps")
        debug and print(f"Candidates paths was at most {max_paths_length}")
        assert best_complete_double_path is not None
        return best_complete_double_path.current_value

    finally:
        if debug:
            busiest_functions = sorted(TIMERS, key=lambda k: TIMERS[k])[-3:]
            for func_key in busiest_functions:
                print(f"{func_key}: {TIMERS[func_key]}")
            print(sum(TIMERS.values()))


def parse_line(line: str) -> tuple[Valve, list[str]]:
    match = re.match(LINE_REGEX, line)
    assert match, line
    name, rate, connections = match.groups()
    return Valve(name, int(rate)), connections.split(", ")


def visited_key(double_path: DoublePath) -> tuple[frozenset[Valve], frozenset[Valve]]:
    return (frozenset(double_path.valves_opened), frozenset(double_path.location))
