from dataclasses import dataclass
from typing import Literal

import pytest


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Sensor(Point):
    beacon: "Beacon"

    @property
    def distance(self) -> int:
        return manhattan(self, self.beacon)

    def chop_bound(self, bound: "SafeBound") -> list["SafeBound"]:
        return []


class Beacon(Point):
    pass


@dataclass
class SafeBound:
    p1: Point
    p2: Point

    @property
    def m(self) -> Literal[-1, 1]:
        return 1 if (self.p1.x < self.p2.x) == (self.p1.y < self.p2.y) else -1

    def closest_point(self, point: Point) -> tuple[float, float]:
        """
        y = m(x - x1) + y1 = mx - m*x1 + y1
        y = -m*(x - xp) + yp = -mx + m*xp + yp
        y1 - yp - m(x1 + xp) = -2mx
        (y1 - yp - m(x1 + xp)) / (-2m)
        """
        x = (self.p1.y - point.y - self.m * (self.p1.x + point.x)) / (-2 * self.m)
        y = self.m * (x - self.p1.x) + self.p1.y
        return (x, y)


def manhattan(p1: Point, p2: Point) -> int:
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


@pytest.mark.parametrize(
    "sensor, bound, new_bounds",
    [
        (
            Sensor(0, 0, Beacon(0, 2)),
            SafeBound(Point(0, 0), Point(3, 3)),
            [SafeBound(Point(2, 2), Point(3, 3))],
        )
    ],
)
def test_chop_bound(sensor: Sensor, bound: SafeBound, new_bounds: list[SafeBound]):
    assert sensor.chop_bound(bound) == new_bounds


def test_closest_point() -> None:
    assert SafeBound(Point(0, 4), Point(4, 0)).closest_point(Point(0, 0)) == (2.0, 2.0)
    assert SafeBound(Point(0, 3), Point(3, 0)).closest_point(Point(0, 0)) == (1.5, 1.5)
