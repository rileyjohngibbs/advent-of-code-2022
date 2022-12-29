from dataclasses import dataclass
from typing import Iterator


def alpha(inputs: list[str], debug: bool = False) -> tuple[int, int]:
    cubes = map(parse_input_line, inputs)
    faces: set[frozenset[Cube]] = set()
    first_cube = parse_input_line(inputs[0])
    bounding_box: tuple[tuple[int, int, int], tuple[int, int, int]] = (
        (first_cube.x - 1, first_cube.y - 1, first_cube.z - 1),
        (first_cube.x + 1, first_cube.y + 1, first_cube.z + 1),
    )
    for cube in cubes:
        for face in cube.faces:
            if face in faces:
                faces.remove(face)
            else:
                faces.add(face)
        bounding_box = (
            (
                min(cube.x - 1, bounding_box[0][0]),
                min(cube.y - 1, bounding_box[0][1]),
                min(cube.z - 1, bounding_box[0][2]),
            ),
            (
                max(cube.x + 1, bounding_box[1][0]),
                max(cube.y + 1, bounding_box[1][1]),
                max(cube.z + 1, bounding_box[1][2]),
            ),
        )
    part1 = len(faces)

    def cube_in_box(cube: Cube) -> bool:
        return (
            bounding_box[0][0] <= cube.x <= bounding_box[1][0]
            and bounding_box[0][1] <= cube.y <= bounding_box[1][1]
            and bounding_box[0][2] <= cube.z <= bounding_box[1][2]
        )

    visited: set[frozenset[Cube]] = set()
    frontier: set[Cube] = {Cube(*bounding_box[0])}
    exterior_faces = 0
    while frontier:
        new_frontier: set[Cube] = set()
        for cube in frontier:
            for neighbor in cube.neigbors():
                face = frozenset([cube, neighbor])
                if face in visited:
                    continue
                else:
                    visited.add(face)
                if cube_in_box(neighbor):
                    if face in faces:
                        exterior_faces += 1
                    else:
                        new_frontier.add(neighbor)
        frontier = new_frontier
    part2 = exterior_faces
    return part1, part2


@dataclass(frozen=True)
class Cube:
    x: int
    y: int
    z: int

    @property
    def faces(self) -> list[frozenset["Cube"]]:
        return [frozenset([self, neighbor]) for neighbor in self.neigbors()]

    def neigbors(self) -> Iterator["Cube"]:
        vectors = ((-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1))
        return (Cube(self.x + dx, self.y + dy, self.z + dz) for dx, dy, dz in vectors)


def parse_input_line(input_line: str) -> Cube:
    coords = map(int, input_line.split(","))
    return Cube(*coords)
