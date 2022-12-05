from typing import Iterable


def alpha(inputs: list[str]) -> tuple[int, int]:
    part1 = sum(
        Rucksack.priority(r.common_item()) for r in map(Rucksack.from_input_row, inputs)
    )

    groups = map(Group.from_input_rows, zip(*[iter(inputs)] * 3))
    common_items = (g.common_item() for g in groups)
    part2 = sum(map(Rucksack.priority, common_items))
    return part1, part2


class Rucksack:
    left: str
    right: str

    def __init__(self, left: str, right: str):
        self.left = left
        self.right = right

    @classmethod
    def from_input_row(cls, row: str) -> "Rucksack":
        half = len(row) // 2
        return cls(row[:half], row[half:])

    @classmethod
    def priority(cls, letter: str) -> int:
        if letter.upper() == letter:
            root, base = "A", 27
        else:
            root, base = "a", 1
        return ord(letter) - ord(root) + base

    def common_item(self) -> str:
        return (set(self.left) & set(self.right)).pop()

    def all_types(self) -> set[str]:
        return set(self.left + self.right)


class Group:
    rucksacks: list["Rucksack"]

    def __init__(self, rucksacks: list["Rucksack"]):
        self.rucksacks = rucksacks

    @classmethod
    def from_input_rows(cls, rows: Iterable[str]) -> "Group":
        return cls(list(map(Rucksack.from_input_row, rows)))

    def common_item(self) -> str:
        return set.intersection(*[r.all_types() for r in self.rucksacks]).pop()
