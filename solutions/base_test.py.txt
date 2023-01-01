import os

import pytest

from .solution import alpha

TEST_INPUT_PATH = "inputs/testDAYNO.txt"
EXAMPLE_SOLUTIONS = (0, 0)


@pytest.fixture
def example() -> list[str]:
    if not os.path.exists(TEST_INPUT_PATH):
        raise FileNotFoundError(f"Please add the example at {TEST_INPUT_PATH}")
    with open(TEST_INPUT_PATH) as f:
        return [line.replace("\n", "") for line in f.readlines()]


def test_example(example: list[str]) -> None:
    assert alpha(example) == EXAMPLE_SOLUTIONS
