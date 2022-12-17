from .safebound import Beacon, SafeBound, Sensor
from .utils import manhattan, parse_line


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    sensor_beacon_pairs = list(map(parse_line, inputs))

    scanned_columns: set[int] = set()
    beacon_xs_in_row: set[int] = set()
    ROW = 2000000
    # ROW = 10  # test value
    for sensor_tuple, beacon in sensor_beacon_pairs:
        if beacon[1] == ROW:
            beacon_xs_in_row.add(beacon[0])
        distance_to_row = manhattan(sensor_tuple, (sensor_tuple[0], ROW))
        distance_to_beacon = manhattan(sensor_tuple, beacon)
        radius_at_row = distance_to_beacon - distance_to_row
        scanned_columns.update(
            range(sensor_tuple[0] - radius_at_row, sensor_tuple[0] + radius_at_row + 1)
        )
    scanned_columns.difference_update(beacon_xs_in_row)
    part1 = len(scanned_columns)

    sensors = [
        Sensor(*sensor, Beacon(*beacon)) for sensor, beacon in sensor_beacon_pairs
    ]
    initial_safebounds: set[SafeBound] = set.union(*map(Sensor.safe_bounds, sensors))
    safebounds: set[SafeBound] = initial_safebounds.copy()
    for sensor in sensors:
        safebounds = set.union(*map(sensor.chop_bound, safebounds), set())
    assert len(safebounds) == 1, safebounds
    bound = next(iter(safebounds))
    assert bound.p1 == bound.p2, (bound.p1, bound.p2)
    part2 = bound.p1.x * 4000000 + bound.p1.y

    return part1, part2
