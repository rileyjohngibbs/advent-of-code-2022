def alpha(inputs: list[str]) -> tuple[int, int]:
    elves: list[int] = []
    elf = 0
    for line in inputs:
        if not line:
            elves.append(elf)
            elf = 0
        else:
            elf += int(line)
    elves.append(elf)

    elves.sort()
    part_one = elves[-1]

    part_two = sum(elves[-3:])

    return part_one, part_two
