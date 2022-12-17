import math
from dataclasses import dataclass
from typing import Iterable, Literal, Optional

from .utils import manhattan

MIN_COORD = 0
MAX_COORD = 4_000_000
# MAX_COORD = 20  # testing value


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class Sensor(Point):
    beacon: "Beacon"

    @property
    def radius(self) -> int:
        return manhattan(self, self.beacon)

    def chop_bound(self, bound: "SafeBound") -> set["SafeBound"]:
        closest_point = bound.closest_point(self)
        if bound.left.x <= closest_point[0] <= bound.right.x:
            distance = manhattan(self, closest_point)
        else:
            distance = min(manhattan(self, bound.left), manhattan(self, bound.right))
        if distance <= self.radius:
            x, y = closest_point
            d = self.radius / 2 + 1
            rx = math.floor(x + d)
            ry = int(y + (rx - x) * bound.m)
            right = Point(rx, ry)
            lx = math.ceil(x - d)
            ly = int(y + (lx - x) * bound.m)
            left = Point(lx, ly)
            new_bounds = set(
                filter(
                    SafeBound.is_ordered,
                    (SafeBound(bound.left, left), SafeBound(right, bound.right)),
                )
            )
        else:
            new_bounds = {bound}
        return new_bounds

    def safe_bounds(self) -> set["SafeBound"]:
        north, south, east, west = (
            Point(self.x, self.y + self.radius + 1),
            Point(self.x, self.y - self.radius - 1),
            Point(self.x + self.radius + 1, self.y),
            Point(self.x - self.radius - 1, self.y),
        )
        return set(
            filter(
                None,
                [
                    SafeBound(north, east).box(),
                    SafeBound(south, east).box(),
                    SafeBound(west, south).box(),
                    SafeBound(west, north).box(),
                ],
            )
        )


class Beacon(Point):
    pass


@dataclass(frozen=True)
class SafeBound:
    p1: Point
    p2: Point

    @property
    def m(self) -> Literal[-1, 1]:
        return 1 if (self.p1.x < self.p2.x) == (self.p1.y < self.p2.y) else -1

    def closest_point(self, point: Point) -> tuple[float, float]:
        """
        Returns the closest point on the line, not necessarily on the segment.
        y = m(x - x1) + y1 = mx - m*x1 + y1
        y = -m*(x - xp) + yp = -mx + m*xp + yp
        y1 - yp - m(x1 + xp) = -2mx
        (y1 - yp - m(x1 + xp)) / (-2m)
        """
        x = (self.p1.y - point.y - self.m * (self.p1.x + point.x)) / (-2 * self.m)
        y = self.m * (x - self.p1.x) + self.p1.y
        return (x, y)

    @property
    def left(self) -> Point:
        if self.p1.x <= self.p2.x:
            return self.p1
        else:
            return self.p2

    @property
    def right(self) -> Point:
        if self.left is self.p1:
            return self.p2
        else:
            return self.p1

    @property
    def bottom(self) -> Point:
        if self.p1.y <= self.p2.y:
            return self.p1
        else:
            return self.p2

    @property
    def top(self) -> Point:
        if self.bottom is self.p1:
            return self.p2
        else:
            return self.p1

    def is_ordered(self) -> bool:
        return self.p1.x <= self.p2.x

    def box(self) -> Optional["SafeBound"]:
        if self.left is self.bottom:
            left_trim = max(
                max(MIN_COORD - self.left.x, 0), max(MIN_COORD - self.left.y, 0)
            )
            right_trim = max(
                max(self.right.x - MAX_COORD, 0), max(self.right.y - MAX_COORD, 0)
            )
        else:
            left_trim = max(
                max(MIN_COORD - self.left.x, 0), max(self.left.y - MAX_COORD, 0)
            )
            right_trim = max(
                max(self.right.x - MAX_COORD, 0), max(MIN_COORD - self.right.y, 0)
            )
        new_point = SafeBound(
            Point(self.left.x + left_trim, self.left.y + left_trim * self.m),
            Point(self.right.x - right_trim, self.right.y - right_trim * self.m),
        )
        if not new_point.is_ordered():
            return None
        return new_point


def print_board(bounds: Iterable[SafeBound], sensors: Iterable[Sensor]):
    safe_points = set.union(*map(interpolate, bounds))
    sensor_points = {Point(s.x, s.y) for s in sensors}
    beacon_points = {Point(s.beacon.x, s.beacon.y) for s in sensors}
    for row in range(20, -1, -1):
        for column in range(0, 21):
            p = Point(column, row)
            if p in sensor_points:
                print("S", end="")
            elif p in beacon_points:
                print("B", end="")
            elif p in safe_points:
                print("#", end="")
            else:
                print(".", end="")
        print()


def interpolate(bound: SafeBound) -> set[Point]:
    return {
        Point(bound.left.x + s, bound.left.y + bound.m * s)
        for s in range(bound.right.x - bound.left.x + 1)
    }
