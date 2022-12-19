import pytest

from .models import DoublePath, Path, Valve

LINEAR_NETWORK: dict[Valve, list[Valve]] = {}
valves = [Valve(name=chr(65 + n) * 2, rate=n) for n in range(15)]
for n, valve in enumerate(valves):
    if n == 0:
        LINEAR_NETWORK[valve] = [valves[n + 1]]
    elif n == len(valves) - 1:
        LINEAR_NETWORK[valve] = [valves[n - 1]]
    else:
        LINEAR_NETWORK[valve] = [valves[n - 1], valves[n + 1]]


@pytest.mark.parametrize(
    "path, new_paths",
    [
        pytest.param(
            Path(
                network=LINEAR_NETWORK,
                valves_opened={valves[0]: 1, valves[1]: 3},
                location=valves[1],
                minute=4,
                current_travel=set(),
            ),
            [
                Path(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1, valves[1]: 3},
                    location=valves[0],
                    minute=5,
                    current_travel={valves[1]},
                ),
                Path(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1, valves[1]: 3},
                    location=valves[2],
                    minute=5,
                    current_travel={valves[1]},
                ),
            ],
            id="move left or right",
        ),
        pytest.param(
            Path(
                network=LINEAR_NETWORK,
                valves_opened={valves[0]: 1},
                location=valves[1],
                minute=3,
                current_travel={valves[0]},
            ),
            [
                Path(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1, valves[1]: 3},
                    location=valves[1],
                    minute=4,
                    current_travel=set(),
                ),
                Path(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1},
                    location=valves[2],
                    minute=4,
                    current_travel={valves[0], valves[1]},
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
                minute=29,
                location=valves[0],
                current_travel=set(),
            ),
            14,
        ),
        (
            Path(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=28,
                location=valves[0],
                current_travel=set(),
            ),
            28,
        ),
        (
            Path(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=27,
                location=valves[0],
                current_travel=set(),
            ),
            55,
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
                location=(valves[0], valves[0]),
                current_travel=(set(), set()),
            ),
            [
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1},
                    minute=2,
                    location=(valves[0], valves[1]),
                    current_travel=(set(), {valves[0]}),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={},
                    minute=2,
                    location=(valves[1], valves[1]),
                    current_travel=({valves[0]}, {valves[0]}),
                ),
            ],
            id="first minute, asymmetry",
        ),
        pytest.param(
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={valves[0]: 1},
                minute=2,
                location=(valves[0], valves[1]),
                current_travel=(set(), {valves[0]}),
            ),
            [
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1, valves[1]: 2},
                    minute=3,
                    location=(valves[1], valves[1]),
                    current_travel=({valves[0]}, set()),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1},
                    minute=3,
                    location=(valves[1], valves[2]),
                    current_travel=({valves[0]}, {valves[0], valves[1]}),
                ),
            ],
            id="second minute, one valve opened",
        ),
        pytest.param(
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={valves[0]: 1},
                minute=3,
                location=(valves[1], valves[2]),
                current_travel=({valves[0]}, {valves[1]}),
            ),
            [
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1, valves[1]: 3, valves[2]: 3},
                    minute=4,
                    location=(valves[1], valves[2]),
                    current_travel=(set(), set()),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1, valves[1]: 3},
                    minute=4,
                    location=(valves[1], valves[3]),
                    current_travel=(set(), {valves[1], valves[2]}),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1, valves[2]: 3},
                    minute=4,
                    location=(valves[2], valves[2]),
                    current_travel=({valves[0], valves[1]}, set()),
                ),
                DoublePath(
                    network=LINEAR_NETWORK,
                    valves_opened={valves[0]: 1},
                    minute=4,
                    location=(valves[2], valves[3]),
                    current_travel=({valves[0], valves[1]}, {valves[1], valves[2]}),
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
                location=(valves[0], valves[0]),
                current_travel=(set(), set()),
            ),
            14 + 13,
        ),
        (
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=24,
                location=(valves[0], valves[0]),
                current_travel=(set(), set()),
            ),
            14 * 2 + 13 * 2,
        ),
        (
            DoublePath(
                network=LINEAR_NETWORK,
                valves_opened={},
                minute=23,
                location=(valves[0], valves[0]),
                current_travel=(set(), set()),
            ),
            14 * 3 + 13 * 3 + 12 + 11,
        ),
    ],
)
def test_double_path_maximum_value(path: DoublePath, maximum_value: int) -> None:
    assert path.maximum_value == maximum_value
