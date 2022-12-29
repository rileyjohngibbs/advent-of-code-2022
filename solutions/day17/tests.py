import pytest

from .solution import alpha


@pytest.fixture
def test_input() -> list[str]:
    with open("inputs/test17.txt") as f:
        return list(map(str.strip, f.readlines()))


def test_solution(test_input: list[str]) -> None:
    assert alpha(test_input, False) == (3068, 1514285714288)
