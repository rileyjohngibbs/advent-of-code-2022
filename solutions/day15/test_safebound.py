import pytest

from .safebound import Beacon, Point, SafeBound, Sensor


@pytest.mark.parametrize(
    "sensor, bound, new_bounds",
    [
        pytest.param(
            Sensor(0, 0, Beacon(0, 2)),
            SafeBound(Point(0, 0), Point(3, 3)),
            {SafeBound(Point(2, 2), Point(3, 3))},
            id="cut left end, m+",
        ),
        pytest.param(
            Sensor(2, 3, Beacon(2, 4)),
            SafeBound(Point(0, 0), Point(3, 3)),
            {SafeBound(Point(0, 0), Point(1, 1))},
            id="cut right end, m+",
        ),
        pytest.param(
            Sensor(2, 0, Beacon(0, 0)),
            SafeBound(Point(0, 3), Point(3, 0)),
            {SafeBound(Point(0, 3), Point(1, 2))},
            id="cut right end, m-",
        ),
        pytest.param(
            Sensor(0, 2, Beacon(0, 3)),
            SafeBound(Point(0, 3), Point(3, 0)),
            {SafeBound(Point(2, 1), Point(3, 0))},
            id="cut left end, m-",
        ),
        pytest.param(
            Sensor(0, 0, Beacon(0, 1)),
            SafeBound(Point(-1, 2), Point(2, -1)),
            {
                SafeBound(Point(-1, 2), Point(-1, 2)),
                SafeBound(Point(2, -1), Point(2, -1)),
            },
            id="cut in the middle",
        ),
        pytest.param(
            Sensor(0, 0, Beacon(0, 3)),
            SafeBound(Point(0, 2), Point(2, 0)),
            set(),
            id="envelope completely",
        ),
        pytest.param(
            Sensor(0, 0, Beacon(0, 3)),
            SafeBound(Point(1, 1), Point(5, 5)),
            {SafeBound(Point(2, 2), Point(5, 5))},
        ),
        pytest.param(
            Sensor(0, 0, Beacon(0, 4)),
            SafeBound(Point(1, 1), Point(5, 5)),
            {SafeBound(Point(3, 3), Point(5, 5))},
        ),
        pytest.param(
            Sensor(x=2, y=0, beacon=Beacon(x=2, y=10)),
            SafeBound(p1=Point(x=11, y=14), p2=Point(x=17, y=20)),
            {SafeBound(p1=Point(x=11, y=14), p2=Point(x=17, y=20))},
        ),
    ],
)
def test_chop_bound(sensor: Sensor, bound: SafeBound, new_bounds: list[SafeBound]):
    assert sensor.chop_bound(bound) == new_bounds


@pytest.mark.parametrize(
    "bound, point, closest",
    [
        (SafeBound(Point(0, 4), Point(4, 0)), Point(0, 0), (2.0, 2.0)),
        (SafeBound(Point(0, 3), Point(3, 0)), Point(0, 0), (1.5, 1.5)),
        (SafeBound(Point(1, 1), Point(3, 3)), Point(0, 0), (0.0, 0.0)),
        (SafeBound(Point(1, 1), Point(3, 3)), Point(3, 1), (2.0, 2.0)),
    ],
)
def test_closest_point(
    bound: SafeBound, point: Point, closest: tuple[float, float]
) -> None:
    assert bound.closest_point(point) == closest


@pytest.mark.parametrize(
    "bound, new_bound",
    [
        (SafeBound(Point(-2, 0), Point(2, 4)), SafeBound(Point(0, 2), Point(2, 4))),
        (SafeBound(Point(-2, 4), Point(2, 0)), SafeBound(Point(0, 2), Point(2, 0))),
        (SafeBound(Point(-2, 0), Point(0, -2)), None),
    ],
)
def test_box(bound: SafeBound, new_bound: SafeBound) -> None:
    assert bound.box() == new_bound


@pytest.mark.parametrize(
    "sensor, bounds",
    [
        (
            Sensor(0, 0, Beacon(0, 2)),
            {
                SafeBound(Point(0, 3), Point(0, 3)),
                SafeBound(Point(0, 3), Point(3, 0)),
                SafeBound(Point(3, 0), Point(3, 0)),
            },
        ),
        (
            Sensor(2, 2, Beacon(1, 1)),
            {
                SafeBound(Point(0, 1), Point(1, 0)),
                SafeBound(Point(0, 3), Point(2, 5)),
                SafeBound(Point(2, 5), Point(5, 2)),
                SafeBound(Point(3, 0), Point(5, 2)),
            },
        ),
    ],
)
def test_safe_bounds(sensor: Sensor, bounds: set[SafeBound]):
    assert sensor.safe_bounds() == bounds
