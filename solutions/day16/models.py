from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from itertools import islice, product
from typing import Iterator, TypeVar

TIME_LIMIT = 30


@dataclass(frozen=True)
class Valve:
    name: str
    rate: int

    def __repr__(self) -> str:
        return f"<Valve {self.name} ({self.rate})>"


T_ = TypeVar("T_")


class Network:
    connections: dict[str, tuple[Valve, ...]]
    valves: dict[str, Valve]
    _dist_cache: dict[tuple[str, str], int]

    def __init__(self, valves: dict[str, Valve], connections: list[tuple[str, str]]):
        self.connections = {}
        self.valves = valves
        for from_, to_ in connections:
            self.connections[valves[from_].name] = self.connections.get(
                valves[from_].name, ()
            ) + (valves[to_],)
        self._dist_cache = {}

    def __iter__(self) -> Iterator[Valve]:
        return (v for v in self.valves.values())

    def get_connections(self, valve_name: str) -> tuple[Valve, ...]:
        return self.connections[valve_name]

    @cached_property
    def sorted_valves(self) -> tuple[Valve, ...]:
        return tuple(sorted(self.valves.values(), key=lambda v: v.rate, reverse=True))

    def distance(self, start: Valve, end: Valve) -> int:
        key = (start.name, end.name)
        if key in self._dist_cache:
            return self._dist_cache[key]

        visited = {start.name}
        frontier: list[Valve] = list(self.get_connections(start.name))
        steps = 0
        best_path: int | None = None
        while end.name not in visited:
            if not frontier:
                if best_path:
                    steps = best_path
                    break
                else:
                    raise Exception()
            new_frontier = [
                conn
                for valve in frontier
                for conn in self.get_connections(valve.name)
                if conn.name not in visited
            ]
            visited.update(v.name for v in frontier)
            steps += 1

            frontier = []
            pre_calced: int | None = None
            for valve in new_frontier:
                valve_key = (valve.name, end.name)
                if valve_key not in self._dist_cache:
                    frontier.append(valve)
                else:
                    pre_calced = (
                        min(pre_calced, self._dist_cache[valve_key] + steps + 1)
                        if pre_calced is not None
                        else self._dist_cache[valve_key] + steps + 1
                    )

            if pre_calced is not None:
                if best_path is None or best_path > pre_calced:
                    best_path = pre_calced
            if best_path == steps:
                break

        self._dist_cache[key] = steps
        self._dist_cache[(key[1], key[0])] = steps
        return steps


class BasePath(ABC):
    network: Network
    valves_opened: dict[Valve, int]
    minute: int
    location: tuple[Valve, Valve] | Valve
    current_travel: tuple[set[Valve], set[Valve]] | set[Valve]
    time_limit: int
    _max_value_cache: int | None = None

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
    def maximum_value(self) -> int:
        if self._max_value_cache is not None:
            return self._max_value_cache
        value = self.calculate_maximum_value()
        self._max_value_cache = value
        return value

    @abstractmethod
    def calculate_maximum_value(self) -> int:
        ...

    @abstractmethod
    def next_iterations(self: T_) -> list[T_]:
        ...


@dataclass
class Path(BasePath):
    network: Network
    valves_opened: dict[Valve, int]
    minute: int
    location: Valve
    current_travel: set[Valve]
    time_limit: int = TIME_LIMIT

    def calculate_maximum_value(self) -> int:
        initial_move = self.location in self.valves_opened
        max_valves_opened = (self.time_left - initial_move) // 2
        best_valves = islice(
            (
                valve
                for valve in self.network.sorted_valves
                if valve not in self.valves_opened
                and self.network.distance(self.location, valve) < self.time_left - 1
            ),
            max_valves_opened,
        )
        return self.current_value + sum(
            (self.time_left - initial_move - (rank * 2 + 1)) * valve.rate
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
        opener = (
            self.location not in self.valves_opened
            and self.location.rate != 0
            and [self.open()]
            or []
        )
        neighbors = (
            valve
            for valve in self.network.get_connections(self.location.name)
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


@dataclass
class DoublePath(BasePath):
    network: Network
    valves_opened: dict[Valve, int]
    minute: int
    location: tuple[Valve, Valve]
    current_travel: tuple[set[Valve], set[Valve]]
    time_limit: int = TIME_LIMIT - 4

    def __repr__(self) -> str:
        return super().__repr__()

    def calculate_maximum_value(self) -> int:
        initial_move = self.location in self.valves_opened
        max_valves_opened = (self.time_left - initial_move) // 2 * 2
        best_valves = islice(
            (
                valve
                for valve in self.network.sorted_valves
                if valve not in self.valves_opened
                and (
                    self.network.distance(self.location[0], valve) < self.time_left - 1
                    or self.network.distance(self.location[1], valve)
                    < self.time_left - 1
                )
            ),
            max_valves_opened,
        )
        value = self.current_value + sum(
            (self.time_left - initial_move - (rank // 2 * 2 + 1)) * valve.rate
            for rank, valve in enumerate(best_valves)
        )
        return value

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
        if all(
            valve.rate == 0 or valve in self.valves_opened for valve in self.network
        ):
            return [
                DoublePath(
                    network=self.network,
                    valves_opened=self.valves_opened,
                    minute=self.time_limit + 1,
                    location=self.location,
                    current_travel=self.current_travel,
                )
            ]

        human, elephant = self.location
        human_travel, elephant_travel = self.current_travel
        if (
            self.noop_valve(human)
            and all(
                neighbor in human_travel
                for neighbor in self.network.get_connections(human.name)
            )
            or self.noop_valve(elephant)
            and all(
                neighbor in elephant_travel
                for neighbor in self.network.get_connections(elephant.name)
            )
        ):
            return []
        human_moves: list[Valve | None] = [
            valve
            for valve in self.network.get_connections(human.name)
            if valve not in human_travel
        ]
        elephant_moves: list[Valve | None] = [
            valve
            for valve in self.network.get_connections(elephant.name)
            if valve not in elephant_travel
        ]
        if human not in self.valves_opened and human.rate != 0:
            human_moves.append(None)
        if (
            elephant not in self.valves_opened
            and elephant != human
            and elephant.rate != 0
        ):
            elephant_moves.append(None)

        iterations: list[DoublePath] = []
        for hum, ele in product(human_moves, elephant_moves):
            action = self.act(human_move=hum, elephant_move=ele)
            if action.minute < self.time_limit + 1 and action.noop_state():
                iterations.extend(action.next_iterations())
            else:
                iterations.append(action)
        return iterations

    def noop_state(self) -> bool:
        return self.noop_valve(self.location[0]) and self.noop_valve(self.location[1])

    def noop_valve(self, valve: Valve) -> bool:
        return valve.rate == 0 or valve in self.valves_opened

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
