def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    grid = [[0 for _ in row] for row in inputs]
    single_start: set[tuple[int, int]] = {(-1, -1)}
    multiple_start: set[tuple[int, int]] = set()
    end = (-1, -1)
    for i, row in enumerate(inputs):
        for j, item in enumerate(row):
            match item:
                case "S":
                    grid[i][j] = ord("a")
                    single_start = {(i, j)}
                    multiple_start.add((i, j))
                case "E":
                    grid[i][j] = ord("z")
                    end = (i, j)
                case "a":
                    grid[i][j] = ord(item)
                    multiple_start.add((i, j))
                case _:
                    grid[i][j] = ord(item)
    part1 = pathfind(grid, single_start, end)
    part2 = pathfind(grid, multiple_start, end)
    return part1, part2


def pathfind(
    grid: list[list[int]], start: set[tuple[int, int]], end: tuple[int, int]
) -> int:
    visited: set[tuple[int, int]] = set()
    frontier = start
    steps = 0
    while end not in visited:
        new_frontier: set[tuple[int, int]] = set()
        for y, x in frontier:
            new_frontier.update(valid_neighbors(grid, y, x).difference(visited))
            visited.add((y, x))
        steps += 1
        frontier = new_frontier
    return steps - 1


def valid_neighbors(grid: list[list[int]], y: int, x: int) -> set[tuple[int, int]]:
    start_value = grid[y][x]
    candidates = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
    return {
        (y_, x_)
        for y_, x_ in candidates
        if 0 <= y_ < len(grid)
        and 0 <= x_ < len(grid[0])
        and grid[y_][x_] <= start_value + 1
    }
