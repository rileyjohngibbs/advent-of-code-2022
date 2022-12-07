def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    stream = inputs[0]
    part1 = first_unique_sequence(stream, 4, debug)
    part2 = first_unique_sequence(stream, 14, debug)
    return part1, part2


def first_unique_sequence(stream: str, length: int, debug: bool) -> int:
    sequence = list(stream[:length])
    for i, char in enumerate(stream[length:], length):
        if debug:
            print(sequence)
        if len(set(sequence)) == length:
            break
        sequence.append(char)
        sequence.pop(0)
    return i


def beta(inputs: list[str], debug: bool) -> tuple[int, int]:
    stream = inputs[0]

    def find_unique(n: int) -> int:
        return next(i for i in range(len(stream)) if len(set(stream[i - n : i])) == n)

    part1 = find_unique(4)
    part2 = find_unique(14)
    return part1, part2
