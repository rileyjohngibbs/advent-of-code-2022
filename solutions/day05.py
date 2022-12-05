import re


def alpha(inputs: list[str], debug: bool = False) -> tuple[str, str]:
    break_line = inputs.index("")
    diagram = inputs[:break_line]
    instructions = inputs[break_line + 1 :]

    crane = Crane(diagram)
    crane.do_all_instructions(instructions, debug=debug)
    part1 = crane.top_crates

    adv_crane = Crane(diagram, advanced=True)
    adv_crane.do_all_instructions(instructions, debug=debug)
    part2 = adv_crane.top_crates

    return part1, part2


class Crane:
    stacks: list[list[str]]
    advanced: bool

    INSTRUCTION_RE = r"move (?P<num>\d+) from (?P<orig>\d+) to (?P<dest>\d+)"

    def __init__(self, diagram: list[str], advanced: bool = False):
        count = len(diagram[-1].split())
        self.stacks = [[] for _ in range(count)]
        for row in diagram[-2::-1]:
            for i, crate in enumerate(row[1::4]):
                if crate != " ":
                    self.stacks[i].append(crate)
        self.advanced = advanced

    @property
    def top_crates(self) -> str:
        return "".join(s[-1] for s in self.stacks)

    def do_all_instructions(self, instructions: list[str], debug: bool = False):
        if debug:
            self.print_state()
        for instruction in instructions:
            self.do_instruction(instruction)
            if debug:
                self.print_state()

    def print_state(self) -> None:
        for i, s in enumerate(self.stacks):
            print(f"{i + 1}: {s}")
        print("==========")

    def do_instruction(self, instruction: str):
        m = re.match(self.INSTRUCTION_RE, instruction)
        if m is None:
            raise ValueError()
        origin = self.stacks[int(m.group("orig")) - 1]
        destination = self.stacks[int(m.group("dest")) - 1]
        number = int(m.group("num"))
        if not self.advanced:
            for _ in range(number):
                destination.append(origin.pop())
        else:
            destination.extend(origin[-number:])
            origin[-number:] = []
