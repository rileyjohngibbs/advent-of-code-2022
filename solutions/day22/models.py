from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Any


@dataclass(frozen=True)
class Point:
    y: int
    x: int

    def __add__(self, other: Any) -> "Point":
        if isinstance(other, Direction):
            match other:
                case Direction.RIGHT:
                    return Point(self.y, self.x + 1)
                case Direction.LEFT:
                    return Point(self.y, self.x - 1)
                case Direction.UP:
                    return Point(self.y - 1, self.x)
                case Direction.DOWN:
                    return Point(self.y + 1, self.x)
        else:
            raise TypeError()


class Turn(Enum):
    L = -1
    R = 1


class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

    def turn(self, t: Turn | None) -> "Direction":
        if t is None:
            return self
        return Direction((self.value + t.value) % 4)


class Map:
    walkables: set[Point]
    walls: set[Point]
    all_tiles: set[Point]
    bottom_right: Point
    position: Point
    direction: Direction

    def __init__(self, walkables: set[Point], walls: set[Point]):
        self.walkables = walkables
        self.walls = walls
        self.all_tiles = walkables | walls

        max_y, max_x = 0, 0
        for coord in self.all_tiles:
            max_y = max(coord.y, max_y)
            max_x = max(coord.x, max_x)
        self.bottom_right = Point(max_y, max_x)

        self.position = min(
            (coord for coord in walkables if coord.y == 1), key=lambda c: c.x
        )
        self.direction = Direction.RIGHT

    def advance(self, steps: int):
        for _ in range(steps):
            next_point = self.position + self.direction
            if next_point not in self.all_tiles:
                next_point = self.wrap_around(next_point)
            if next_point in self.walls:
                break
            else:
                self.position = next_point

    def turn(self, turn: Turn | None):
        self.direction = self.direction.turn(turn)

    def wrap_around(self, point: Point) -> Point:
        match self.direction:
            case Direction.RIGHT:
                next_point = next(
                    coord
                    for x in range(self.bottom_right.x + 1)
                    if (coord := Point(point.y, x)) in self.all_tiles
                )
            case Direction.LEFT:
                next_point = next(
                    coord
                    for x in range(self.bottom_right.x, 0, -1)
                    if (coord := Point(point.y, x)) in self.all_tiles
                )
            case Direction.DOWN:
                next_point = next(
                    coord
                    for y in range(self.bottom_right.y + 1)
                    if (coord := Point(y, point.x)) in self.all_tiles
                )
            case Direction.UP:
                next_point = next(
                    coord
                    for y in range(self.bottom_right.y, 0, -1)
                    if (coord := Point(y, point.x)) in self.all_tiles
                )
        return next_point
