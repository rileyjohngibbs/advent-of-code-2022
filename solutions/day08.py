def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    visible: set[tuple[int, int]] = set()
    rows = [list(map(int, row)) for row in inputs]
    columns: list[list[int]] = list(map(list, zip(*rows)))
    for ri, row in enumerate(rows):
        visible.update((ri, ci) for ci in visible_indices(row, debug))
    for ci, column in enumerate(columns):
        visible.update((ri, ci) for ri in visible_indices(column, debug))

    part1 = len(visible)
    part2 = max(
        viewing_score(rows, ri, ci, debug)
        for ri in range(len(rows))
        for ci in range(len(rows[0]))
    )
    return part1, part2


def visible_indices(row: list[int], debug: bool) -> list[int]:
    i, j = 0, len(row) - 1
    mi, mj = -1, -1
    visible: list[int] = []
    while i <= j:
        if row[i] > mi:
            visible.append(i)
            mi = row[i]
            i += 1
        elif row[i] <= mj:
            i += 1
        elif row[j] > mj:
            visible.append(j)
            mj = row[j]
            j -= 1
        elif row[j] <= mi:
            j -= 1
        else:
            raise ValueError("wtf this shouldn't be possible")
    if debug:
        visible.sort()
        print(row)
        print(visible)
        print([row[v] for v in visible])
    return visible


def viewing_score(grid: list[list[int]], ri: int, ci: int, debug: bool = False) -> int:
    center = grid[ri][ci]
    height = len(grid)
    width = len(grid[0])

    def _look(dr: int, dc: int) -> int:
        distance = 0
        ri_ = ri + dr
        ci_ = ci + dc
        while 0 <= ri_ < height and 0 <= ci_ < width and grid[ri_][ci_] < center:
            distance += 1
            ri_ += dr
            ci_ += dc
        if 0 <= ri_ < height and 0 <= ci_ < width:
            distance += 1
        return distance

    north = _look(-1, 0)
    south = _look(1, 0)
    west = _look(0, -1)
    east = _look(0, 1)
    if debug:
        print((ri, ci), north, south, west, east)
    return north * south * west * east
