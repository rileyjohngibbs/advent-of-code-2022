import os
from functools import reduce

import pytest

from .models import Blueprint, FactoryState, Resource, ResourceSet
from .solution import alpha, build_initial_state, parse_blueprint

TEST_INPUT_PATH = "inputs/test19.txt"
EXAMPLE_SOLUTIONS = (33, 0)


@pytest.fixture
def example() -> list[str]:
    if not os.path.exists(TEST_INPUT_PATH):
        raise FileNotFoundError(f"Please add the example at {TEST_INPUT_PATH}")
    with open(TEST_INPUT_PATH) as f:
        return [line.replace("\n", "") for line in f.readlines()]


@pytest.fixture
def example_blueprint_1(example: list[str]) -> Blueprint:
    return parse_blueprint(example[0])


def test_example(example: list[str]) -> None:
    # assert False
    assert alpha(example) == EXAMPLE_SOLUTIONS


# @pytest.mark.parametrize(
#     "minutes, resources",
#     [
#         (3, ResourceSet(ore=1)),
#         (24, ResourceSet(6, 41, 8, 9)),
#         (5, ResourceSet(1, 2)),
#         (18, ResourceSet(2, 17, 3)),
#         (19, ResourceSet(3, 21, 5, 1)),
#         (20, ResourceSet(4, 25, 7, 2)),
#         (21, ResourceSet(3, 29, 2, 3)),
#     ],
# )
def test_example_blueprint_1(example: list[str]) -> None:
    state = build_initial_state(example[0])
    builds: list[tuple[int, Resource | None]] = [
        (2, Resource.CLAY),
        (2, Resource.CLAY),
        (2, Resource.CLAY),
        (4, Resource.OBSIDIAN),
        (1, Resource.CLAY),
        (3, Resource.OBSIDIAN),
        (3, Resource.GEODE),
        (3, Resource.GEODE),
        (4, None),
    ]
    final_state = reduce(
        lambda s, b: s.gather(b[0]).build(b[1]) if b[1] is not None else s.gather(b[0]),
        builds,
        state,
    )
    assert final_state.resources == ResourceSet(6, 41, 8, 9)


def test_branch(example_blueprint_1: Blueprint) -> None:
    state = FactoryState(example_blueprint_1, ResourceSet(), ResourceSet(1))
    assert state.branch(24) == {
        (
            FactoryState(
                example_blueprint_1, ResourceSet(), ResourceSet(1), ResourceSet(0, 1)
            ),
            22,
        ),
        (
            FactoryState(
                example_blueprint_1, ResourceSet(), ResourceSet(1), ResourceSet(1)
            ),
            20,
        ),
    }


def test_turns_to_save(example_blueprint_1: Blueprint) -> None:
    state = FactoryState(example_blueprint_1, ResourceSet(), ResourceSet(1))
    assert state.turns_to_save(Resource.ORE) == 4
    assert state.turns_to_save(Resource.CLAY) == 2
