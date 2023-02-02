from .models import Map, Point, Turn


def alpha(inputs: list[str], debug: bool = False) -> tuple[int, int]:
    map_, path = parse_inputs(inputs)
    for steps, turn in path:
        map_.advance(steps)
        map_.turn(turn)
        debug and print(map_.position, map_.direction)
    part1 = map_.position.y * 1000 + map_.position.x * 4 + map_.direction.value
    part2 = 0
    return part1, part2


def parse_inputs(inputs: list[str]) -> tuple[Map, list[tuple[int, Turn | None]]]:
    map_lines = inputs[:-2]
    directions_line = inputs[-1]

    walkables: set[Point] = set()
    walls: set[Point] = set()
    for y, row in enumerate(map_lines, 1):
        for x, value in enumerate(row, 1):
            if value == ".":
                walkables.add(Point(y, x))
            elif value == "#":
                walls.add(Point(y, x))
    map = Map(walkables=walkables, walls=walls)

    current_value = ""
    path: list[tuple[int, Turn | None]] = []
    for c in directions_line:
        if c.isalpha():
            path.append((int(current_value), Turn[c]))
            current_value = ""
        else:
            current_value += c
    path.append((int(current_value), None))

    return map, path
