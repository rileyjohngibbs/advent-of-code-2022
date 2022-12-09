from enum import Enum
from typing import Any


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    movements = (
        (Direction[letter], int(count)) for letter, count in map(str.split, inputs)
    )
    head_address = Address((0, 0))
    tails = [Tail(debug and x == 8) for x in range(9)]
    for direction, count in movements:
        for _ in range(count):
            head_address += direction.value
            lead = head_address
            for tail in tails:
                tail.follow(lead)
                lead = tail.address
            if debug:
                print(f"h: {head_address}")
    part1 = len(tails[0].visited)
    part2 = len(tails[-1].visited)
    return part1, part2


def beta(inputs: list[str], debug: bool) -> tuple[int, int]:
    movements = (
        (Direction[letter], int(count)) for letter, count in map(str.split, inputs)
    )
    knots = [Address((0, 0)) for _ in range(10)]
    second_visits = {Address((0, 0))}
    tenth_visits = {Address((0, 0))}
    for direction, count in movements:
        for _ in range(count):
            knots[0] += direction.value
            for k in range(1, 10):
                knots[k] = knots[k].follow(knots[k - 1])
            if debug and knots[9] not in tenth_visits:
                print(knots[9])
            second_visits.add(knots[1])
            tenth_visits.add(knots[9])
            if debug:
                print(f"h: {knots[0]}")
    part1 = len(second_visits)
    part2 = len(tenth_visits)
    return part1, part2


class Direction(Enum):
    R = (1, 0)
    L = (-1, 0)
    U = (0, 1)
    D = (0, -1)


class Address(tuple[int, int]):
    def __add__(self, other: Any) -> "Address":
        if type(other) is tuple:
            return Address(s + o for s, o in zip(self, other))
        else:
            raise TypeError()

    def follow(self, other: "Address") -> "Address":
        dx, dy = [o - s for o, s in zip(other, self)]
        if not (-2 < dx < 2 and -2 < dy < 2):
            delta = (dx and dx // abs(dx), dy and dy // abs(dy))
            return self + delta
        else:
            return self


class Tail:
    address: Address
    visited: set[Address]
    debug: bool

    def __init__(self, debug: bool = False) -> None:
        self.address = Address((0, 0))
        self.visited = {self.address}
        self.debug = debug

    def follow(self, head_address: tuple[int, int]) -> None:
        dx, dy = [h - t for h, t in zip(head_address, self.address)]
        if not (-2 < dx < 2 and -2 < dy < 2):
            self.address += (dx and dx // abs(dx), dy and dy // abs(dy))
            if self.debug and self.address not in self.visited:
                print(self.address)
            self.visited.add(self.address)
