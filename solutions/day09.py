from enum import Enum
from typing import Any


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    movements = (
        (Direction[letter], int(count)) for letter, count in map(str.split, inputs)
    )
    head_address = Address((0, 0))
    tails = [Tail(debug) for _ in range(9)]
    for direction, count in movements:
        for _ in range(count):
            head_address += direction.value
            lead = head_address
            for tail in tails:
                tail.follow(lead)
                lead = tail.address
    part1 = len(tails[0].visited)
    part2 = len(tails[-1].visited)
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
            self.visited.add(self.address)
        if self.debug:
            print(self.address)
