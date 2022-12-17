from typing import TYPE_CHECKING, Protocol, overload

if TYPE_CHECKING:
    from .safebound import Point


def parse_line(line: str) -> tuple[tuple[int, int], tuple[int, int]]:
    sensor_str, beacon_str = line.split(": ")
    sx, sy = [int(s[2:]) for s in sensor_str.removeprefix("Sensor at ").split(", ")]
    bx, by = [
        int(s[2:]) for s in beacon_str.removeprefix("closest beacon is at ").split(", ")
    ]
    return (sx, sy), (bx, by)


@overload
def manhattan(p1: "Point" | tuple[int, int], p2: "Point" | tuple[int, int]) -> int:
    ...


@overload
def manhattan(
    p1: "Point" | tuple[int, int] | tuple[float, float], p2: tuple[float, float]
) -> float:
    ...


@overload
def manhattan(
    p1: tuple[float, float], p2: "Point" | tuple[int, int] | tuple[float, float]
) -> float:
    ...


def manhattan(
    p1: "Point" | tuple[float, float] | tuple[int, int],
    p2: "Point" | tuple[float, float] | tuple[int, int],
) -> int | float:
    x1: int | float
    y1: int | float
    x2: int | float
    y2: int | float
    if isinstance(p1, tuple):
        x1, y1 = p1
    else:
        x1, y1 = p1.x, p1.y
    if isinstance(p2, tuple):
        x2, y2 = p2
    else:
        x2, y2 = p2.x, p2.y
    return abs(x1 - x2) + abs(y1 - y2)
