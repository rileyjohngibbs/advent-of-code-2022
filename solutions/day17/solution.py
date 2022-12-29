from dataclasses import dataclass
from itertools import cycle
from typing import Any, Callable, Iterator, Optional

ROCK_PATTERN = """
####

.#.
###
.#.

..#
..#
###

#
#
#
#

##
##
"""


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    jets = list(map(direction_factory, inputs[0]))
    chamber = Chamber(jets)
    while chamber.rock_count < 2022:
        chamber.tick()
    part1 = chamber.highest_point

    new_chamber = Chamber(jets)
    pattern = False
    jet_count = len(jets)
    rock_count = len(ROCKS)
    cycle_count = 0
    delta = (0, 0)
    while not pattern:
        base = (new_chamber.highest_point, new_chamber.rock_count)
        for _ in range(jet_count * rock_count):
            new_chamber.tick()
        new_delta = (
            new_chamber.highest_point - base[0],
            new_chamber.rock_count - base[1],
        )
        if new_delta == delta:
            pattern = True
        delta = new_delta
        cycle_count += 1
        debug and print(cycle_count, delta)
    remaining_rocks = 1_000_000_000_000 - new_chamber.rock_count
    remaining_cycles = remaining_rocks // delta[1]
    virtual_pile_height = remaining_cycles * delta[0]
    remainder = remaining_rocks % delta[1]
    target = new_chamber.rock_count + remainder
    while new_chamber.rock_count < target:
        new_chamber.tick()
    part2 = new_chamber.highest_point + virtual_pile_height
    return part1, part2


class Chamber:
    WIDTH = 7

    highest_point: int
    rock_spawn: Iterator[set["Point"]]
    rock_count: int
    rock: Optional["Rock"]
    jets: Iterator[Callable[["Rock"], "Rock"]]
    pile: set["Point"]

    def __init__(self, jets: list[Callable[["Rock"], "Rock"]]) -> None:
        self.highest_point = 0
        self.rock_spawn = cycle(ROCKS)
        self.rock_count = 0
        self.rock = None
        self.jets = cycle(jets)
        self.pile = {Point(0, x) for x in range(self.WIDTH)}

    def print(self) -> None:
        pass

    def tick(self) -> None:
        if self.rock is None:
            self.rock = Rock(next(self.rock_spawn), Point(self.highest_point + 4, 2))
        jet_rock = next(self.jets)(self.rock)
        if all(map(self.empty, jet_rock.points)):
            self.rock = jet_rock
        fall_rock = self.rock.down()
        if all(map(self.empty, fall_rock.points)):
            self.rock = fall_rock
        else:
            self.pile |= self.rock.points
            self.highest_point = max(
                max(p.y for p in self.rock.points), self.highest_point
            )
            self.rock = None
            self.rock_count += 1

    def empty(self, point: "Point") -> bool:
        return 0 <= point.x < self.WIDTH and point not in self.pile


class Rock:
    locus: "Point"
    shape: "Shape"

    def __init__(self, shape: "Shape", locus: Optional["Point"] = None):
        self.locus = locus if locus is not None else Point(0, 0)
        self.shape = shape

    def left(self) -> "Rock":
        return Rock(self.shape, self.locus.left())

    def right(self) -> "Rock":
        return Rock(self.shape, self.locus.right())

    def down(self) -> "Rock":
        return Rock(self.shape, self.locus.down())

    @property
    def points(self) -> set["Point"]:
        return {s_point + self.locus for s_point in self.shape}


Shape = set["Point"]


@dataclass(frozen=True)
class Point:
    y: int
    x: int

    def left(self) -> "Point":
        return Point(self.y, self.x - 1)

    def right(self) -> "Point":
        return Point(self.y, self.x + 1)

    def down(self) -> "Point":
        return Point(self.y - 1, self.x)

    def __add__(self, other: Any) -> "Point":
        if not isinstance(other, Point):
            raise TypeError()
        return Point(self.y + other.y, self.x + other.x)


FLAT = {Point(0, 0), Point(0, 1), Point(0, 2), Point(0, 3)}
PLUS = {Point(0, 1), Point(1, 0), Point(1, 1), Point(1, 2), Point(2, 1)}
ELL = {Point(0, 0), Point(0, 1), Point(0, 2), Point(1, 2), Point(2, 2)}
BAR = {Point(0, 0), Point(1, 0), Point(2, 0), Point(3, 0)}
BOX = {Point(0, 0), Point(0, 1), Point(1, 0), Point(1, 1)}

ROCKS = [FLAT, PLUS, ELL, BAR, BOX]


def direction_factory(symbol: str) -> Callable[["Rock"], "Rock"]:
    if symbol == "<":
        return Rock.left
    return Rock.right
