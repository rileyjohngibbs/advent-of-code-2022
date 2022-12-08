def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    rows = [list(map(int, row)) for row in inputs]
    columns: list[list[int]] = transpose(rows)

    visible: set[tuple[int, int]] = set()
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


def beta(inputs: list[str], debug: bool) -> tuple[int, int]:
    rows = [list(map(int, row)) for row in inputs]
    columns: list[list[int]] = transpose(rows)

    # part1 is the same as alpha
    visible: set[tuple[int, int]] = set()
    for ri, row in enumerate(rows):
        visible.update((ri, ci) for ci in visible_indices(row, debug))
    for ci, column in enumerate(columns):
        visible.update((ri, ci) for ri in visible_indices(column, debug))
    part1 = len(visible)

    # part2 is different
    left_scores = [row_viewing_scores(row) for row in rows]
    right_scores = [row_viewing_scores(row[::-1])[::-1] for row in rows]
    up_scores = transpose([row_viewing_scores(col) for col in columns])
    down_scores = transpose([row_viewing_scores(col[::-1])[::-1] for col in columns])
    scores = [
        [left * right * up * down for left, right, up, down in zip(*row_scores)]
        for row_scores in zip(left_scores, right_scores, up_scores, down_scores)
    ]
    part2 = max(max(*row) for row in scores)

    return part1, part2


def transpose(grid: list[list[int]]) -> list[list[int]]:
    return list(map(list, zip(*grid)))


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


def row_viewing_scores(row: list[int]) -> list[int]:
    """
    Defining `boundaries` as a list instead of a dict saved some time.
    Updating `boundaries` in the for loop with list multiplication instead of a
    list comprehension, `[x for _ in range(height + 1)]`, saved even more!
    """
    boundaries = [0 for _ in range(10)]
    distances: list[int] = []
    for x, height in enumerate(row):
        distances.append(x - boundaries[height])
        boundaries[: height + 1] = [x] * (height + 1)
        # Original implementation, much slower!
        # boundaries[: height + 1] = [x for _ in range(height + 1)]
    return distances
