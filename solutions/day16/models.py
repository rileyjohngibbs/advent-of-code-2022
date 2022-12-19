from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TypeVar

TIME_LIMIT = 30


@dataclass(frozen=True)
class Valve:
    name: str
    rate: int

    def __repr__(self) -> str:
        return f"<Valve {self.name} ({self.rate})>"


Network = dict[Valve, list[Valve]]
T_ = TypeVar("T_")


class BasePath(ABC):
    network: Network
    valves_opened: dict[Valve, int]
    minute: int
    location: tuple[Valve, Valve] | Valve
    current_travel: tuple[set[Valve], set[Valve]] | set[Valve]
    time_limit: int

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: valves_opened={self.valves_opened}, minute={self.minute}, "
            f"location={self.location}, current_travel={self.current_travel}>"
        )

    @cached_property
    def current_value(self) -> int:
        return sum(
            valve.rate * (self.time_limit - minute)
            for valve, minute in self.valves_opened.items()
        )

    @property
    def time_left(self) -> int:
        return self.time_limit - self.minute + 1

    @property
    def complete(self) -> bool:
        return self.minute > self.time_limit

    @property
    @abstractmethod
    def maximum_value(self) -> int:
        ...

    @abstractmethod
    def next_iterations(self: T_) -> list[T_]:
        ...


@dataclass(frozen=True)
class Path(BasePath):
    network: Network
    valves_opened: dict[Valve, int]
    minute: int
    location: Valve
    current_travel: set[Valve]
    time_limit: int = TIME_LIMIT

    @cached_property
    def maximum_value(self) -> int:
        max_valves_opened = self.time_left // 2
        best_valves = sorted(
            [valve for valve in self.network if valve not in self.valves_opened],
            key=lambda v: v.rate,
            reverse=True,
        )[:max_valves_opened]
        return self.current_value + sum(
            (self.time_left - (rank * 2 + 1)) * valve.rate
            for rank, valve in enumerate(best_valves)
        )

    def next_iterations(self) -> list["Path"]:
        if self.minute == self.time_limit:
            return [
                Path(
                    network=self.network,
                    valves_opened={**self.valves_opened},
                    minute=self.minute + 1,
                    location=self.location,
                    current_travel={*self.current_travel},
                )
            ]
        opener = self.location not in self.valves_opened and [self.open()] or []
        neighbors = (
            valve
            for valve in self.network[self.location]
            if valve not in self.current_travel
        )
        return opener + list(map(self.move, neighbors))

    def open(self) -> "Path":
        valves_opened = {self.location: self.minute, **self.valves_opened}
        return self.act(valves_opened=valves_opened, current_travel=set())

    def move(self, valve: Valve) -> "Path":
        return self.act(
            location=valve, current_travel={self.location, *self.current_travel}
        )

    def act(
        self,
        *,
        valves_opened: dict[Valve, int] | None = None,
        location: Valve | None = None,
        current_travel: set[Valve],
    ) -> "Path":
        new_opened = (
            valves_opened is not None and valves_opened or {**self.valves_opened}
        )
        new_location = location is not None and location or self.location
        return Path(
            network=self.network,
            valves_opened=new_opened,
            minute=self.minute + 1,
            location=new_location,
            current_travel=current_travel,
        )


@dataclass(frozen=True)
class DoublePath(BasePath):
    network: Network
    valves_opened: dict[Valve, int]
    minute: int
    location: tuple[Valve, Valve]
    current_travel: tuple[set[Valve], set[Valve]]
    time_limit: int = TIME_LIMIT - 4

    def __repr__(self) -> str:
        return super().__repr__()

    @cached_property
    def maximum_value(self) -> int:
        max_valves_opened = self.time_left // 2 * 2
        best_valves = sorted(
            [valve for valve in self.network if valve not in self.valves_opened],
            key=lambda v: v.rate,
            reverse=True,
        )[:max_valves_opened]
        return self.current_value + sum(
            (self.time_left - (rank // 2 * 2 + 1)) * valve.rate
            for rank, valve in enumerate(best_valves)
        )

    def next_iterations(self) -> list["DoublePath"]:
        if self.minute == self.time_limit:
            return [
                DoublePath(
                    network=self.network,
                    valves_opened=self.valves_opened,
                    minute=self.minute + 1,
                    location=self.location,
                    current_travel=self.current_travel,
                )
            ]

        human, elephant = self.location
        human_travel, elephant_travel = self.current_travel
        human_moves: list[Valve | None] = [
            valve for valve in self.network[human] if valve not in human_travel
        ]
        elephant_moves: list[Valve | None] = [
            valve for valve in self.network[elephant] if valve not in elephant_travel
        ]
        if human not in self.valves_opened:
            human_moves.append(None)
        if elephant not in self.valves_opened and elephant != human:
            elephant_moves.append(None)

        iterations = [
            self.act(human_move=hum, elephant_move=ele)
            for hum in human_moves
            for ele in elephant_moves
        ]
        return iterations

    def act(
        self, *, human_move: Valve | None = None, elephant_move: Valve | None = None
    ) -> "DoublePath":
        if human_move is None:
            human_open = {self.location[0]: self.minute}
            human_location = self.location[0]
            human_travel = set()
        else:
            human_open = {}
            human_location = human_move
            human_travel = {self.location[0]} | self.current_travel[0]
        if elephant_move is None:
            elephant_open = {self.location[1]: self.minute}
            elephant_location = self.location[1]
            elephant_travel = set()
        else:
            elephant_open = {}
            elephant_location = elephant_move
            elephant_travel = {self.location[1]} | self.current_travel[1]
        valves_opened = (
            (human_open or elephant_open)
            and human_open | elephant_open | self.valves_opened
            or self.valves_opened
        )
        return DoublePath(
            network=self.network,
            valves_opened=valves_opened,
            minute=self.minute + 1,
            location=(human_location, elephant_location),
            current_travel=(human_travel, elephant_travel),
        )
