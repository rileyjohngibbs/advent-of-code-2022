from typing import Protocol


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    instructions_lookup: dict[str, Instruction] = {
        func.__name__: func for func in (noop, addx)
    }
    register = 1
    strength = 0
    cycle_values = []
    for instr_name, *args in map(str.split, inputs):
        new_register, dc = instructions_lookup[instr_name](register, *args)
        cycle_values.extend([register] * dc)
        register = new_register

    cycle_points = [20, 60, 100, 140, 180, 220]
    strength = sum(point * cycle_values[point - 1] for point in cycle_points)
    part1 = strength

    # Part 2 is visual and the answer must be read from stdout
    if debug:
        s = "\n".join(map("-".join, zip(*[map(str, cycle_values)] * 40)))
        print(s)
    lit_gen = (abs(reg - (i % 40)) <= 1 for i, reg in enumerate(cycle_values))
    screen: list[list[str]] = [[]]
    for lit in lit_gen:
        if len(screen[-1]) == 40:
            screen.append([])
        if lit:
            screen[-1].append("#")
        else:
            screen[-1].append(" ")
    image = "\n".join(map("".join, screen))
    print(image)

    part2 = 0
    return part1, part2


class Instruction(Protocol):
    def __call__(self, value: int, *args: str) -> tuple[int, int]:
        ...


def noop(value: int, *_: str) -> tuple[int, int]:
    return value, 1


def addx(value: int, *args: str) -> tuple[int, int]:
    return value + int(args[0]), 2
