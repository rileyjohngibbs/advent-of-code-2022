from functools import cached_property
from typing import Callable, overload

BinaryOp = Callable[[int, int], int]


class Monkey:
    name: str
    number: int | None
    operands: tuple[str, str] | None
    operation: BinaryOp | None

    _all_monkeys: dict[str, "Monkey"] = {}

    @overload
    def __init__(self, name: str, *, number: int):
        ...

    @overload
    def __init__(
        self,
        name: str,
        *,
        operands: tuple[str, str],
        operation: BinaryOp,
    ):
        ...

    def __init__(
        self,
        name: str,
        *,
        number: int | None = None,
        operands: tuple[str, str] | None = None,
        operation: BinaryOp | None = None,
    ):
        self.name = name
        self.number = number
        self.operands = operands
        self.operation = operation
        self._all_monkeys[self.name] = self

    def callout(self) -> int:
        if self.number is not None:
            return self.number
        elif self.operands is not None and self.operation is not None:
            operands = (m.callout() for m in map(self.get_monkey, self.operands))
            return self.operation(*operands)
        else:
            raise TypeError()

    @classmethod
    def get_monkey(cls, name: str) -> "Monkey":
        return cls._all_monkeys[name]

    @cached_property
    def contains_humn(self) -> bool:
        return (
            self.name == "humn"
            or self.operands is not None
            and any(self.get_monkey(op).contains_humn for op in self.operands)
        )

    def balance(self, value: int) -> int:
        if self.name == "humn":
            return value
        assert self.operands is not None and self.operation is not None
        left, right = tuple(map(self.get_monkey, self.operands))
        assert left.contains_humn != right.contains_humn
        humn_side = left if left.contains_humn else right
        mnky_side = left if right is humn_side else right
        mnky_value = mnky_side.callout()
        if self.operation is add:
            humn_value = subtract(value, mnky_value)
        elif self.operation is subtract:
            if mnky_side is left:
                humn_value = subtract(mnky_value, value)
            else:
                humn_value = add(value, mnky_value)
        elif self.operation is multiply:
            humn_value = divide(value, mnky_value)
        elif self.operation is divide:
            if mnky_side is left:
                humn_value = divide(mnky_value, value)
            else:
                humn_value = multiply(value, mnky_value)
        else:
            raise ValueError()
        return humn_side.balance(humn_value)


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b


def divide(a: int, b: int) -> int:
    return a // b
