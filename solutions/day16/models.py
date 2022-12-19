from dataclasses import dataclass
from functools import cached_property

TIME_LIMIT = 30


@dataclass(frozen=True)
class Valve:
    name: str
    rate: int

    def __repr__(self) -> str:
        return f"<Valve {self.name} ({self.rate})>"


Network = dict[Valve, list[Valve]]


@dataclass(frozen=True)
class Path:
    network: Network
    valves_opened: dict[Valve, int]
    minute: int
    location: Valve
    current_travel: set[Valve]

    def __repr__(self) -> str:
        return (
            f"<Path: valves_opened={self.valves_opened}, minute={self.minute}, "
            f"location={self.location.name}, current_travel={self.current_travel}>"
        )

    @cached_property
    def current_value(self) -> int:
        return sum(
            valve.rate * (TIME_LIMIT - minute)
            for valve, minute in self.valves_opened.items()
        )

    @cached_property
    def maximum_value(self) -> int:
        max_valves_opened = (self.time_left + 1) // 2
        best_valves = sorted(
            [valve for valve in self.network if valve not in self.valves_opened],
            key=lambda v: v.rate,
            reverse=True,
        )[:max_valves_opened]
        return self.current_value + sum(
            (self.time_left - (rank * 2)) * valve.rate
            for rank, valve in enumerate(best_valves)
        )

    @property
    def time_left(self) -> int:
        return TIME_LIMIT - self.minute

    @property
    def complete(self) -> bool:
        return self.minute > TIME_LIMIT

    def next_iterations(self) -> list["Path"]:
        if self.minute == TIME_LIMIT:
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
