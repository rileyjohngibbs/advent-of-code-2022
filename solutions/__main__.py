import sys
from typing import Any, Callable

from . import day01
from .parsing import ArgsModel, build_parser

solutions: dict[int, list[Callable[[list[str]], Any]]] = {1: [day01.alpha]}


def main() -> None:
    parser = build_parser(MainArgs)
    args = parser.parse(sys.argv[1:])
    day_solvers = solutions.get(args.day_number, [])
    if len(day_solvers) <= args.version:
        raise UnsolvedError(args.day_number, args.version)
    solver = day_solvers[args.version]
    with open(args.input_filepath) as f:
        input_strs = f.readlines()
    print(solver(input_strs))


class MainArgs(ArgsModel):
    day_number: int
    input_filepath: str
    version: int = 0

    class Meta:
        flags: dict[str, tuple[str, str] | tuple[str] | str] = {
            "version": ("v", "version")
        }


class UnsolvedError(NotImplementedError):
    def __init__(self, day_number: int, version: int) -> None:
        msg = f"No solution of day {day_number} and version {version}."
        super().__init__(msg)


if __name__ == "__main__":
    main()
