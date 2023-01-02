import re

from .models import Monkey, add, divide, multiply, subtract


def alpha(inputs: list[str], debug: bool = False) -> tuple[int, int]:
    monkeys = list(map(parse_monkey, inputs))
    root = Monkey.get_monkey("root")
    assert root.operands is not None
    part1 = root.callout()

    left, right = list(map(Monkey.get_monkey, root.operands))
    assert left.contains_humn != right.contains_humn
    humn_side = left if left.contains_humn else right
    mnky_side_value = left.callout() if right is humn_side else right.callout()
    part2 = humn_side.balance(mnky_side_value)
    return part1, part2


def parse_monkey(input: str) -> Monkey:
    if input[6].isalpha():
        match = re.match(
            r"(?P<name>.{4}): (?P<operand1>.{4}) (?P<operation>.) (?P<operand2>.{4})",
            input,
        )
        assert match
        match match.group("operation"):
            case "+":
                operation = add
            case "-":
                operation = subtract
            case "*":
                operation = multiply
            case "/":
                operation = divide
            case _:
                raise ValueError()
        monkey = Monkey(
            name=match.group("name"),
            operands=(match.group("operand1"), match.group("operand2")),
            operation=operation,
        )
    else:
        match = re.match(r"(?P<name>.{4}): (?P<number>\d+)", input)
        assert match
        monkey = Monkey(match.group("name"), number=int(match.group("number")))
    return monkey
