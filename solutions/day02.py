from enum import Enum


class Outcome(Enum):
    WIN = 6
    LOSE = 0
    DRAW = 3


class Move(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    def outcome(self, other: "Move") -> Outcome:
        return [Outcome.DRAW, Outcome.WIN, Outcome.LOSE][(self.value - other.value) % 3]


class MoveOpp(Enum):
    A = Move.ROCK
    B = Move.PAPER
    C = Move.SCISSORS


class MoveSelf(Enum):
    X = Move.ROCK
    Y = Move.PAPER
    Z = Move.SCISSORS


class NeededOutcome(Enum):
    X = Outcome.LOSE
    Y = Outcome.DRAW
    Z = Outcome.WIN

    def needed_move(self, other: "Move") -> "Move":
        mod = OUTCOME_TO_MOD[self.value]
        return Move((other.value + mod) % 3 or 3)


OUTCOME_TO_MOD: dict[Outcome, int] = {Outcome.WIN: 1, Outcome.DRAW: 0, Outcome.LOSE: 2}


def alpha(inputs: list[str]) -> tuple[int, int]:
    part1 = sum(round_score_part1(*line.split(" ")) for line in inputs)
    part2 = sum(round_score_part2(*line.split(" ")) for line in inputs)
    return part1, part2


def round_score_part1(opponent: str, self_: str) -> int:
    return (
        MoveSelf[self_].value.outcome(MoveOpp[opponent].value).value
        + MoveSelf[self_].value.value
    )


def round_score_part2(opponent: str, outcome: str) -> int:
    needed_outcome = NeededOutcome[outcome]
    return (
        needed_outcome.needed_move(MoveOpp[opponent].value).value
        + needed_outcome.value.value
    )
