import re


def alpha(inputs: list[str], debug: bool = False) -> tuple[int, int]:
    pairs = list(map(SectionPair.from_input_row, inputs))
    part1 = sum(pair.fully_overlaps() for pair in pairs)
    part2 = sum(pair.overlaps_at_all() for pair in pairs)
    return part1, part2


class SectionPair:
    first: tuple[int, int]
    second: tuple[int, int]

    def __init__(self, first: tuple[int, int], second: tuple[int, int]):
        self.first = first
        self.second = second

    @classmethod
    def from_input_row(cls, row: str) -> "SectionPair":
        m = re.match(r"(\d+)-(\d+),(\d+)-(\d+)", row)
        if m is None:
            raise ValueError()
        return cls(
            (int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4)))
        )

    def fully_overlaps(self) -> bool:
        return (
            self.first[0] <= self.second[0] <= self.second[1] <= self.first[1]
            or self.second[0] <= self.first[0] <= self.first[1] <= self.second[1]
        )

    def overlaps_at_all(self) -> bool:
        return self.first[0] <= self.second[1] and self.second[0] <= self.first[1]
