import sys
import time
from contextlib import contextmanager
from typing import Any, Callable, Iterator

from solutions import (
    day01,
    day02,
    day03,
    day04,
    day05,
    day06,
    day07,
    day08,
    day09,
    day10,
    day11,
    day12,
    day13,
    day14,
    day15,
    day16,
    day17,
    day18,
    day19,
    day20,
)
from solutions.parsing import ArgsModel, build_parser

solution_functions: dict[int, list[Callable[[list[str], bool], Any]]] = {
    1: [day01.alpha],
    2: [day02.alpha],
    3: [day03.alpha],
    4: [day04.alpha],
    5: [day05.alpha],
    6: [day06.alpha, day06.beta],
    7: [day07.alpha],
    8: [day08.alpha, day08.beta],
    9: [day09.alpha, day09.beta],
    10: [day10.alpha],
    11: [day11.alpha],
    12: [day12.alpha],
    13: [day13.alpha],
    14: [day14.alpha],
    15: [day15.alpha],
    16: [day16.alpha],
    17: [day17.alpha],
    18: [day18.alpha],
    19: [day19.alpha],
    20: [day20.alpha],
}


def main() -> None:
    parser = build_parser(MainArgs)
    args = parser.parse(sys.argv[1:])
    day_solvers = solution_functions.get(args.day_number, [])
    if len(day_solvers) <= args.version:
        raise UnsolvedError(args.day_number, args.version)
    solver = day_solvers[args.version]
    with open(args.input_filepath) as f:
        input_strs = [line.replace("\n", "") for line in f.readlines()]
    with timeit(args.timeit):
        print(solver(input_strs, args.debug))


class MainArgs(ArgsModel):
    day_number: int
    input_filepath: str
    version: int = 0
    debug: bool
    timeit: bool

    class Meta:
        flags: dict[str, tuple[str, str] | tuple[str] | str] = {
            "version": ("v", "version"),
        }


class UnsolvedError(NotImplementedError):
    def __init__(self, day_number: int, version: int) -> None:
        msg = f"No solution of day {day_number} and version {version}."
        super().__init__(msg)


@contextmanager
def timeit(print_time: bool) -> Iterator[None]:
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        if print_time:
            print(f"Total runtime: {end - start}")


if __name__ == "__main__":
    main()
