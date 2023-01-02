from dataclasses import dataclass

DECRYPTION_KEY = 811589153


def alpha(inputs: list[str], debug: bool = False) -> tuple[int, int]:
    raw_numbers = list(map(int, inputs))
    part1 = mix(raw_numbers)
    part2 = mix(raw_numbers, 10, DECRYPTION_KEY)
    return part1, part2


def mix(raw_numbers: list[int], remix_count: int = 1, decryption_key: int = 1) -> int:
    numbers: list[Number] = [
        Number(i, n * decryption_key) for i, n in enumerate(raw_numbers)
    ]
    list_length = len(numbers)
    for _ in range(remix_count):
        for number_id in range(list_length):
            index, number = next(
                (index, number)
                for index, number in enumerate(numbers)
                if number.id == number_id
            )
            numbers.pop(index)
            new_index = (index + number.value) % (list_length - 1)
            numbers.insert(new_index, number)
    zero_index = next(i for i, number in enumerate(numbers) if number.value == 0)
    solution_indices = (zero_index + 1000, zero_index + 2000, zero_index + 3000)
    return sum(numbers[i % list_length].value for i in solution_indices)


@dataclass
class Number:
    id: int
    value: int
