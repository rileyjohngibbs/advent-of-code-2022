from typing import NewType


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    cross_section = CrossSection.from_inputs(inputs, debug=debug)
    if debug:
        print(cross_section.walls)
    into_abyss = False
    while not into_abyss:
        settlement = cross_section.drop_sand()
        if settlement is None:
            into_abyss = True
        else:
            cross_section.add_settled_sand(settlement)
    part1 = len(cross_section.settled_sand)

    floored_cross_section = CrossSection.from_inputs(inputs, floor=True, debug=debug)
    blocked = False
    while not blocked:
        settlement = floored_cross_section.drop_sand()
        if settlement is None:
            raise TypeError("Unexpected None for sand settlement with floor")
        floored_cross_section.add_settled_sand(settlement)
        if settlement == floored_cross_section.source:
            blocked = True
    part2 = len(floored_cross_section.settled_sand)
    return part1, part2


X = NewType("X", int)
Y = NewType("Y", int)
Address = NewType("Address", tuple[X, Y])


class CrossSection:
    source: Address = Address((X(500), Y(0)))
    walls: set[Address]
    settled_sand: set[Address]
    abyss_point: Y
    floor_level: Y | None

    def __init__(self, walls: set[Address], floor: bool = False):
        self.walls = walls
        self.settled_sand = set()
        self.abyss_point = max(w[1] for w in self.walls)
        self.floor_level = floor and Y(self.abyss_point + 2) or None

    @classmethod
    def from_inputs(
        cls, inputs: list[str], floor: bool = False, debug: bool = False
    ) -> "CrossSection":
        walls: set[Address] = set()
        for row in inputs:
            addrs = (addr.split(",") for addr in row.split(" -> "))
            points = (Address((X(int(x)), Y(int(y)))) for x, y in addrs)
            first_point = next(points)
            for x2, y2 in points:
                match (x2 == first_point[0], y2 == first_point[1]):
                    case (True, False):
                        sign = (y2 - first_point[1]) // abs(y2 - first_point[1])
                        new_walls = [
                            Address((x2, Y(y_)))
                            for y_ in range(first_point[1], y2, sign)
                        ]
                        walls.update(new_walls)
                    case (False, True):
                        sign = (x2 - first_point[0]) // abs(x2 - first_point[0])
                        new_walls = [
                            Address((X(x_), y2))
                            for x_ in range(first_point[0], x2, sign)
                        ]
                        walls.update(new_walls)
                    case _:
                        raise ValueError(f"{first_point} -> {(x2, y2)}")
                first_point = Address((x2, y2))
            walls.add(first_point)
        return cls(walls, floor)

    def is_clear(self, address: Address) -> bool:
        return (
            address not in self.walls
            and address not in self.settled_sand
            and (self.floor_level is None or address[1] < self.floor_level)
        )

    def has_entered_abyss(self, address: Address) -> bool:
        return self.floor_level is None and address[1] >= self.abyss_point

    def drop_sand(self) -> Address | None:
        sand: Address = self.source
        settled = False
        settlement: Address | None
        while not settled:
            direction = self._falling_direction(sand)
            if direction is None:
                settled = True
                settlement = sand
            elif self.has_entered_abyss(direction):
                settled = True
                settlement = None
            else:
                sand = direction
        return settlement

    def add_settled_sand(self, settlement: Address) -> None:
        self.settled_sand.add(settlement)

    def _falling_direction(self, sand: Address) -> Address | None:
        x, y = sand
        directions = (
            Address((X(x_), Y(y_)))
            for x_, y_ in ((x, y + 1), (x - 1, y + 1), (x + 1, y + 1))
        )
        clear_directions = filter(self.is_clear, directions)
        return next(clear_directions, None)
