from collections.abc import Callable
from dataclasses import dataclass
from functools import partial, reduce
from typing import Iterator


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    outputs: list[int] = []
    for count, reduce_worry in ((20, True), (10_000, False)):
        monkeys = parse_input(iter(inputs), reduce_worry=reduce_worry, debug=debug)
        for _ in range(count):
            for monkey in monkeys:
                for value, target in monkey.inspect_and_throw_all():
                    monkeys[target].catch(value)
        first, second = sorted((m.inspections for m in monkeys), reverse=True)[:2]
        outputs.append(first * second)

    part1, part2 = outputs

    return part1, part2


def parse_input(
    code_lines: Iterator[str], reduce_worry: bool, debug: bool = False
) -> list["Monkey"]:
    monkeys = [
        parse_monkey(code_lines) for line in code_lines if line.startswith("Monkey")
    ]
    modulus = reduce(lambda a, b: a * b.divisor, monkeys, 1)
    if not reduce_worry:
        for monkey in monkeys:
            monkey.modulus = modulus
    return monkeys


def parse_monkey(code_lines: Iterator[str], debug: bool = False) -> "Monkey":
    values = list(
        map(int, next(code_lines).strip().removeprefix("Starting items: ").split(", "))
    )
    operation = parse_operation(next(code_lines))
    divisor = int(next(code_lines).strip().removeprefix("Test: divisible by "))
    true_target = int(next(code_lines).rsplit(" ", 1)[-1])
    false_target = int(next(code_lines).rsplit(" ", 1)[-1])
    return Monkey(
        values=values,
        operation=operation,
        divisor=divisor,
        true_target=true_target,
        false_target=false_target,
        debug=debug,
    )


def parse_operation(line: str) -> Callable[[int], int]:
    op_str, arg_str = line.strip().removeprefix("Operation: new = old ").split()
    match op_str:
        case "*":
            func = mult_op
        case "+":
            func = add_op
        case _:
            raise ValueError(line)
    match arg_str:
        case "old":
            op = auto_op(func)
        case _:
            op = partial(func, int(arg_str))
    return op


def add_op(base: int, arg: int) -> int:
    return base + arg


def mult_op(base: int, arg: int) -> int:
    return base * arg


def auto_op(op_func: Callable[[int, int], int]) -> Callable[[int], int]:
    def op(arg: int) -> int:
        return op_func(arg, arg)

    return op


@dataclass
class Monkey:
    values: list[int]
    operation: Callable[[int], int]
    divisor: int
    true_target: int
    false_target: int
    modulus: int | None = None
    inspections: int = 0
    debug: bool = False

    def inspect_and_throw_all(self) -> list[tuple[int, int]]:
        output = list(map(self.inspect_and_throw_item, self.values))
        self.inspections += len(self.values)
        self.values = []
        return output

    def inspect_and_throw_item(self, value: int) -> tuple[int, int]:
        output_value = self.operation(value) // 3 ** (self.modulus is None)
        target = (
            self.true_target
            if (output_value % self.divisor == 0)
            else self.false_target
        )
        return output_value, target

    def catch(self, value: int) -> None:
        self.values.append(value if self.modulus is None else value % self.modulus)
