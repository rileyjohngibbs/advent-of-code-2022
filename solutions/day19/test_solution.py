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
            FactoryState(example_blueprint_1, ResourceSet(1), ResourceSet(1, 1)),
            21,
        ),
        (
            FactoryState(example_blueprint_1, ResourceSet(1), ResourceSet(2)),
            19,
        ),
        (
            FactoryState(example_blueprint_1, ResourceSet(24), ResourceSet(1)),
            0,
        ),
    }


def test_turns_to_save(example_blueprint_1: Blueprint) -> None:
    state = FactoryState(example_blueprint_1, ResourceSet(), ResourceSet(1))
    assert state.turns_to_save(Resource.ORE) == 4
    assert state.turns_to_save(Resource.CLAY) == 2
