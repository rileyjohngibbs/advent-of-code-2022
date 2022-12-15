from dataclasses import dataclass
from itertools import product
from math import ceil, floor
from typing import Any, Iterator, Literal, NewType, Union, overload

import pytest

from .common import sign


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    sensor_beacon_pairs = list(map(parse_line, inputs))

    debug and print(sensor_beacon_pairs)
    scanned_columns: set[int] = set()
    beacon_xs_in_row: set[int] = set()
    ROW = 2000000  # Different for test (10)
    for sensor, beacon in sensor_beacon_pairs:
        if beacon[1] == ROW:
            beacon_xs_in_row.add(beacon[0])
        distance_to_row = manhattan(sensor, (sensor[0], ROW))
        distance_to_beacon = manhattan(sensor, beacon)
        radius_at_row = distance_to_beacon - distance_to_row
        scanned_columns.update(
            range(sensor[0] - radius_at_row, sensor[0] + radius_at_row + 1)
        )
    scanned_columns.difference_update(beacon_xs_in_row)
    debug and print(sorted(scanned_columns))
    part1 = len(scanned_columns)

    MAXIMUM = 4000000  # Different for test (20)

    def in_bounds(point: tuple[int, int]) -> bool:
        return 0 <= point[0] <= MAXIMUM and 0 <= point[1] <= MAXIMUM

    part2 = 0
    return part1, part2


Sensor = NewType("Sensor", tuple[int, int])
Beacon = NewType("Beacon", tuple[int, int])


@dataclass
class Point:
    x: int
    y: int

    def __repr__(self) -> str:
        return f"<Point: {self.x}, {self.y}>"


P = Point


class Segment:
    a: Point
    b: Point
    m: Literal[-1, 1]

    def __init__(self, a: Point, b: Point):
        self.a = a
        self.b = b
        self.m = 1 if (a.x < b.x) == (a.y < b.y) else -1

    def __repr__(self) -> str:
        return f"<Segment: {self.a}, {self.b}>"

    def __eq__(self, other: Any) -> bool:
        if type(other) is not Segment:
            raise TypeError()
        return (
            other.a == self.a
            and other.b == self.b
            or other.a == self.b
            and other.b == self.a
        )

    def intersection_point(self, other: "Segment") -> tuple[float, float]:
        x = (self.a.y - other.a.y - self.m * self.a.x + other.m * other.a.x) / (
            other.m - self.m
        )
        y = self.m * (x - self.a.x) + self.a.y
        return x, y


S = Segment


@dataclass
class Boundary:
    segment: Segment
    center: Point

    def __repr__(self) -> str:
        return f"<Boundary: {self.segment}, {self.center}>"

    def truncate(self, other: "Boundary") -> list["Boundary"]:
        if self.segment.m != other.segment.m:
            x, y = self.segment.intersection_point(other.segment)
            if self.center.x < x:
                x_int = ceil
                keeper_func = max
            else:
                x_int = floor
                keeper_func = min
            keeper = keeper_func((other.segment.a, other.segment.b), key=lambda p: p.x)
            y_int = ceil if self.center.y < y else floor
            new_boundary = [
                Boundary(Segment(keeper, P(x_int(x), y_int(y))), other.center)
            ]
        else:
            new_boundary = [other]
        return new_boundary

    @property
    def distance(self) -> int:
        return manhattan(self.center, self.segment.a) - 1


B = Boundary


def parse_line(line: str) -> tuple[Sensor, Beacon]:
    sensor_str, beacon_str = line.split(": ")
    sx, sy = [int(s[2:]) for s in sensor_str.removeprefix("Sensor at ").split(", ")]
    bx, by = [
        int(s[2:]) for s in beacon_str.removeprefix("closest beacon is at ").split(", ")
    ]
    return Sensor((sx, sy)), Beacon((bx, by))


def manhattan(a: Point | tuple[int, int], b: Point | tuple[int, int]) -> int:
    a_x, a_y = (a.x, a.y) if isinstance(a, Point) else a
    b_x, b_y = (b.x, b.y) if isinstance(b, Point) else b
    return abs(a_x - b_x) + abs(a_y + b_y)


def border(center: tuple[int, int], distance: int) -> set[tuple[int, int]]:
    points: set[tuple[int, int]] = set()
    noon_x, noon_y = center[0], center[1] + distance + 1
    six_x, six_y = center[0], center[1] - distance - 1
    for step in range(distance + 2):
        points.add((noon_x + step, noon_y - step))
        points.add((noon_x - step, noon_y - step))
        points.add((six_x + step, six_y + step))
        points.add((six_x - step, six_y + step))
    return points


@pytest.mark.parametrize(
    "bnd_a, bnd_b, new_a, new_b",
    [
        (  # Overlapping segments
            B(S(P(0, 0), P(2, 2)), P(2, 0)),
            B(S(P(0, 0), P(2, 2)), P(0, 2)),
            [B(S(P(0, 0), P(2, 2)), P(2, 0))],
            [B(S(P(0, 0), P(2, 2)), P(0, 2))],
        ),
        (  # Intersecting at integer coords
            B(S(P(0, 0), P(2, 2)), P(2, 0)),
            B(S(P(0, 2), P(2, 0)), P(0, 0)),
            [B(S(P(1, 1), P(2, 2)), P(2, 0))],
            [B(S(P(0, 2), P(1, 1)), P(0, 0))],
        ),
        (  # Intersecting at non-integer coords
            B(S(P(0, 0), P(3, 3)), P(3, 0)),
            B(S(P(0, 3), P(3, 0)), P(0, 0)),
            [B(S(P(2, 2), P(3, 3)), P(3, 0))],
            [B(S(P(0, 3), P(1, 2)), P(0, 0))],
        ),
        (  # One envelopes the other
            B(S(P(0, 0), P(3, 3)), P(3, 0)),
            B(S(P(1, 0), P(3, 2)), P(3, 0)),
            [B(S(P(0, 0), P(3, 3)), P(3, 0))],
            [],
        ),
        # (  # One cuts the other in two
        #     B(S(P(0, 0), P(3, 3)), P(3, 0)),
        #     B(S(P()))
        # )
    ],
)
def test_truncate(bnd_a: Boundary, bnd_b: Boundary, new_a: Boundary, new_b: Boundary):
    assert bnd_a.truncate(bnd_b) == new_b
    assert bnd_b.truncate(bnd_a) == new_a


def test_intersection() -> None:
    s1 = Segment(P(0, 0), P(3, 3))
    s2 = Segment(P(2, 0), P(0, 2))
    assert s1.intersection_point(s2) == (1.0, 1.0)


def test_m() -> None:
    assert Segment(P(0, 0), P(3, 3)).m == 1
    assert Segment(P(0, 3), P(3, 0)).m == -1
