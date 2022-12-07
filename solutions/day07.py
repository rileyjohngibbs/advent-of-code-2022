from dataclasses import dataclass
from functools import reduce
from typing import Union, cast


def alpha(inputs: list[str], debug: bool) -> tuple[int, int]:
    root = build_file_tree(inputs)
    total_size, subdir_sizes = root.size

    threshold = 100_000
    part1 = sum(dir_size for dir_size in subdir_sizes if dir_size <= threshold)

    capacity = 70_000_000
    space_needed = 30_000_000
    must_delete = total_size - (capacity - space_needed)
    part2 = min(dir_size for dir_size in subdir_sizes if dir_size >= must_delete)

    return part1, part2


@dataclass
class Directory:
    files: dict[str, Union["Directory", int]]

    @property
    def size(self) -> tuple[int, list[int]]:
        size_ = 0
        subdirs: list[int] = []
        for item in self.files.values():
            if type(item) is int:
                size_ += item
            elif type(item) is Directory:
                inner_size, inner_subdirs = item.size
                size_ += inner_size
                subdirs.extend(inner_subdirs)
                subdirs.append(inner_size)
        return size_, subdirs

    def setdefault(self, key: str, value: Union["Directory", int]) -> None:
        self.files.setdefault(key, value)


def build_file_tree(commands: list[str]) -> Directory:
    root: Directory = Directory({})
    current_path: list[str] = []
    for command in commands:
        match command.split():
            case ["$", "ls"]:
                pass
            case ["$", "cd", "/"]:
                current_path = []
            case ["$", "cd", ".."]:
                current_path.pop()
            case ["$", "cd", dirname]:
                workdir(root, current_path).setdefault(dirname, Directory({}))
                current_path.append(command.rsplit(maxsplit=1)[-1])
            case ["dir", dirname]:
                workdir(root, current_path).setdefault(dirname, Directory({}))
            case [filesize, filename]:
                workdir(root, current_path).setdefault(filename, int(filesize))
            case _:
                raise ValueError(command)
    return root


def workdir(root: Directory, current_path: list[str]) -> Directory:
    return reduce(
        lambda dir, dirname: cast(Directory, dir.files[dirname]), current_path, root
    )


def directory_sizes(outer_dir: Directory) -> tuple[list[int], int]:
    subdirs: list[int] = []
    size = 0
    for item in outer_dir.files.values():
        if type(item) is int:
            size += item
        else:
            inner_subdirs, inner_size = directory_sizes(outer_dir)
            subdirs.extend(inner_subdirs)
            size += inner_size
    return subdirs, size
