from itertools import zip_longest
import json
from typing import Any, Iterator, Union


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    pairings = [
        (Packet.build(json.loads(left)), Packet.build(json.loads(right)))
        for left, right, _ in zip_longest(*[iter(inputs)] * 3)
    ]
    if debug:
        for left, right in pairings:
            print(left, right)
            print(left < right)
    part1 = sum(i for i, (left, right) in enumerate(pairings, 1) if left < right)

    dividers = [Packet(Packet(Value(2))), Packet(Packet(Value(6)))]
    packets = [
        Packet.build(json.loads(line)) for line in inputs if line.strip()
    ] + dividers
    packets.sort()
    indices = [
        next((i for i, packet in enumerate(packets, 1) if packet is div))
        for div in dividers
    ]
    part2 = indices[0] * indices[1]

    return part1, part2


class Value:
    value: int

    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if type(other) is Value:
            return self.value == other.value
        if type(other) is Packet:
            return other == self
        raise TypeError(f"Cannot compare {self.__class__} and {other.__class__}")

    def __lt__(self, other: Any) -> bool:
        if type(other) is Value:
            return self.value < other.value
        if type(other) is Packet:
            return Packet(self) < other
        raise TypeError(f"Cannot compare {self.__class__} and {other.__class__}")

    def __repr__(self) -> str:
        return str(self.value)


ListInt = list[Union[int, "ListInt"]]


class Packet:
    items: list[Union[Value, "Packet"]]

    def __init__(self, *items: Union[Value, "Packet"]) -> None:
        self.items = list(items)

    def __iter__(self) -> Iterator[Union[Value, "Packet"]]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __lt__(self, other: Any) -> bool:
        if type(other) is Value:
            return self < Packet(other)
        if type(other) is Packet:
            a, b = next(((a, b) for a, b in zip(self, other) if a != b), (None, None))
            if a is not None and b is not None:
                return a < b
            return len(self) < len(other)
        raise TypeError(f"Cannot compare {self.__class__} and {other.__class__}")

    def __eq__(self, other: Any) -> bool:
        if type(other) is Value:
            return self == Packet(other)
        if type(other) is Packet:
            return self.items == other.items
        raise TypeError(f"Cannot compare {self.__class__} and {other.__class__}")

    def __repr__(self) -> str:
        return self.items.__repr__()

    @classmethod
    def build(cls, input: int | ListInt) -> Union[Value, "Packet"]:
        if type(input) is int:
            return Value(input)
        if type(input) is list:
            return cls(*[cls.build(i) for i in input])
        raise TypeError(f"Cannot build {cls.__name__} from {input.__class__}")


def test_shorter() -> None:
    assert Packet() < Packet(Value(3))
