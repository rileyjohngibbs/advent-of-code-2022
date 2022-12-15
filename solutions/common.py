from typing import Literal


def sign(value: int) -> Literal[-1, 0, 1]:
    return -1 if value < 0 else 1 if value > 0 else 0
