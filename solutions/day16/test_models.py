import pytest

from .models import DoublePath, Network, Path, Valve


def build_linear_network() -> tuple[Network, list[Valve]]:
    valves = [Valve(name=chr(65 + n) * 2, rate=n) for n in range(15)]
    valves_by_name: dict[str, Valve] = {}
    connections: list[tuple[str, str]] = []
    for n, valve in enumerate(valves):
        if n == 0:
            connections.append((valve.name, valves[n + 1].name))
        elif n == len(valves) - 1:
            connections.append((valve.name, valves[n - 1].name))
        else:
            connections.extend(
                [(valve.name, valves[n - 1].name), (valve.name, valves[n + 1].name)]
            )
        valves_by_name[valve.name] = valve
    return Network(valves_by_name, connections), valves


LINEAR_NETWORK, LINEAR_VALVES = build_linear_network()


def build_zeros_network() -> tuple[Network, list[Valve]]:
    valves = [
        Valve(name=chr(65 + n) * 2, rate=(n in (5, 10) and 1 or 0)) for n in range(11)
    ]
    valves_by_name: dict[str, Valve] = {}
    connections: list[tuple[str, str]] = []
    for n, valve in enumerate(valves):
        if n == 0:
            connections.append((valve.name, valves[n + 1].name))
        elif n == len(valves) - 1:
            connections.append((valve.name, valves[n - 1].name))
        else:
            connections.extend(
                [(valve.name, valves[n - 1].name), (valve.name, valves[n + 1].name)]
            )
        valves_by_name[valve.name] = valve
    return Network(valves_by_name, connections), valves


ZEROS_NETWORK, ZEROS_VALVES = build_zeros_network()


@pytest.mark.parametrize(
    "path, new_paths",
    [
        pytest.param(
            Path(
                network=LINEAR_NETWORK,
                valves_opened={LINEAR_VALVES[0]: 1, LINEAR_VALVES[1]: 3},
                location=LINEAR_VALVES[1],
                minute=4,
                current_travel=set(),
            ),
            [
                Path(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1, LINEAR_VALVES[1]: 3},
                    location=LINEAR_VALVES[0],
                    minute=5,
                    current_travel={LINEAR_VALVES[1]},
                ),
                Path(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1, LINEAR_VALVES[1]: 3},
                    location=LINEAR_VALVES[2],
                    minute=5,
                    current_travel={LINEAR_VALVES[1]},
                ),
            ],
            id="move left or right",
        ),
        pytest.param(
            Path(
                network=LINEAR_NETWORK,
                valves_opened={LINEAR_VALVES[0]: 1},
                location=LINEAR_VALVES[1],
                minute=3,
                current_travel={LINEAR_VALVES[0]},
            ),
            [
                Path(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1, LINEAR_VALVES[1]: 3},
                    location=LINEAR_VALVES[1],
                    minute=4,
                    current_travel=set(),
                ),
                Path(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1},
                    location=LINEAR_VALVES[2],
                    minute=4,
                    current_travel={LINEAR_VALVES[0], LINEAR_VALVES[1]},
                ),
            ],
            id="don't go back",
        ),
    ],
)
def test_path_next_iterations(path: Path, new_paths: list[Path]) -> None:
    iterations = path.next_iterations()
    left_only = [p for p in iterations if p not in new_paths]
    right_only = [p for p in new_paths if p not in iterations]
    assert (left_only, right_only) == ([], [])


@pytest.mark.parametrize(
    "path, maximum_value",
    [
        (
            Path(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=28,
                location=LINEAR_VALVES[0],
                current_travel=set(),
            ),
            2,
        ),
        (
            Path(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=27,
                location=LINEAR_VALVES[0],
                current_travel=set(),
            ),
            2 * 3 + 1 * 1,
        ),
        (
            Path(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=26,
                location=LINEAR_VALVES[0],
                current_travel=set(),
            ),
            3 * 4 + 2 * 2,
        ),
    ],
)
def test_path_maximum_value(path: Path, maximum_value: int) -> None:
    assert path.maximum_value == maximum_value


@pytest.mark.parametrize(
    "path, new_paths",
    [
        pytest.param(
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=1,
                location=(LINEAR_VALVES[0], LINEAR_VALVES[0]),
                current_travel=(set(), set()),
            ),
            [
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1},
                    minute=2,
                    location=(LINEAR_VALVES[0], LINEAR_VALVES[1]),
                    current_travel=(set(), {LINEAR_VALVES[0]}),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={},
                    minute=2,
                    location=(LINEAR_VALVES[1], LINEAR_VALVES[1]),
                    current_travel=({LINEAR_VALVES[0]}, {LINEAR_VALVES[0]}),
                ),
            ],
            id="first minute, asymmetry",
        ),
        pytest.param(
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={LINEAR_VALVES[0]: 1},
                minute=2,
                location=(LINEAR_VALVES[0], LINEAR_VALVES[1]),
                current_travel=(set(), {LINEAR_VALVES[0]}),
            ),
            [
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1, LINEAR_VALVES[1]: 2},
                    minute=3,
                    location=(LINEAR_VALVES[1], LINEAR_VALVES[1]),
                    current_travel=({LINEAR_VALVES[0]}, set()),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1},
                    minute=3,
                    location=(LINEAR_VALVES[1], LINEAR_VALVES[2]),
                    current_travel=(
                        {LINEAR_VALVES[0]},
                        {LINEAR_VALVES[0], LINEAR_VALVES[1]},
                    ),
                ),
            ],
            id="second minute, one valve opened",
        ),
        pytest.param(
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={LINEAR_VALVES[0]: 1},
                minute=3,
                location=(LINEAR_VALVES[1], LINEAR_VALVES[2]),
                current_travel=({LINEAR_VALVES[0]}, {LINEAR_VALVES[1]}),
            ),
            [
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={
                        LINEAR_VALVES[0]: 1,
                        LINEAR_VALVES[1]: 3,
                        LINEAR_VALVES[2]: 3,
                    },
                    minute=4,
                    location=(LINEAR_VALVES[1], LINEAR_VALVES[2]),
                    current_travel=(set(), set()),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1, LINEAR_VALVES[1]: 3},
                    minute=4,
                    location=(LINEAR_VALVES[1], LINEAR_VALVES[3]),
                    current_travel=(set(), {LINEAR_VALVES[1], LINEAR_VALVES[2]}),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1, LINEAR_VALVES[2]: 3},
                    minute=4,
                    location=(LINEAR_VALVES[2], LINEAR_VALVES[2]),
                    current_travel=({LINEAR_VALVES[0], LINEAR_VALVES[1]}, set()),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={LINEAR_VALVES[0]: 1},
                    minute=4,
                    location=(LINEAR_VALVES[2], LINEAR_VALVES[3]),
                    current_travel=(
                        {LINEAR_VALVES[0], LINEAR_VALVES[1]},
                        {LINEAR_VALVES[1], LINEAR_VALVES[2]},
                    ),
                ),
            ],
            id="both can open",
        ),
    ],
)
def test_double_path_next_iterations(
    path: DoublePath, new_paths: list[DoublePath]
) -> None:
    iterations = path.next_iterations()
    left_only = [p for p in iterations if p not in new_paths]
    right_only = [p for p in new_paths if p not in iterations]
    assert (left_only, right_only) == ([], [])


@pytest.mark.parametrize(
    "path, maximum_value",
    [
        (
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=25,
                location=(LINEAR_VALVES[0], LINEAR_VALVES[0]),
                current_travel=(set(), set()),
            ),
            0 * 1,  # Cannot reach any non-zero valves
        ),
        (
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=24,
                location=(LINEAR_VALVES[0], LINEAR_VALVES[0]),
                current_travel=(set(), set()),
            ),
            1 * 2,
        ),
        (
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=23,
                location=(LINEAR_VALVES[0], LINEAR_VALVES[0]),
                current_travel=(set(), set()),
            ),
            2 * 3 + 1 * 3,
        ),
        (
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=22,
                location=(LINEAR_VALVES[0], LINEAR_VALVES[0]),
                current_travel=(set(), set()),
            ),
            (3 * 4 + 2 * 4) + (1 * 2 + 0 * 2),
        ),
    ],
)
def test_double_path_maximum_value(path: DoublePath, maximum_value: int) -> None:
    assert path.maximum_value == maximum_value


def test_caching_distance() -> None:
    network, valves = build_linear_network()
    assert network.distance(valves[4], valves[8]) == 4
    assert (valves[4].name, valves[8].name) in network._dist_cache
    assert network._dist_cache[(valves[4].name, valves[8].name)] == 4
    assert (valves[8].name, valves[4].name) in network._dist_cache
    assert network._dist_cache[(valves[8].name, valves[4].name)] == 4
    assert network.distance(valves[0], valves[8]) == 8
