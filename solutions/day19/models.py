import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, Iterator, TypeVar


class Resource(Enum):
    ORE = 0
    CLAY = 1
    OBSIDIAN = 2
    GEODE = 3

    @classmethod
    def for_robots(cls) -> list["Resource"]:
        return [cls.ORE, cls.CLAY, cls.OBSIDIAN]


@dataclass(frozen=True)
class ResourceSet:
    ore: int = 0
    clay: int = 0
    obsidian: int = 0
    geode: int = 0

    def __add__(self, other: Any) -> "ResourceSet":
        if isinstance(other, ResourceSet):
            return ResourceSet(
                self.ore + other.ore,
                self.clay + other.clay,
                self.obsidian + other.obsidian,
                self.geode + other.geode,
            )
        elif isinstance(other, Resource):
            return self + ResourceSet(**{other.name.lower(): 1})
        else:
            raise TypeError(f"Cannot add {self.__class__.__name__} and {type(other)}")

    def __sub__(self, other: Any) -> "ResourceSet":
        if isinstance(other, ResourceSet):
            return ResourceSet(
                self.ore - other.ore,
                self.clay - other.clay,
                self.obsidian - other.obsidian,
                self.geode - other.geode,
            )
        elif isinstance(other, Resource):
            return self - ResourceSet(**{other.name.lower(): 1})
        else:
            raise TypeError(
                f"Cannot subtract {self.__class__.__name__} and {type(other)}"
            )

    def __neg__(self) -> "ResourceSet":
        return ResourceSet(-self.ore, -self.clay, -self.obsidian, -self.geode)

    def __mul__(self, other: Any) -> "ResourceSet":
        if isinstance(other, int):
            return ResourceSet(
                self.ore * other,
                self.clay * other,
                self.obsidian * other,
                self.geode * other,
            )
        else:
            raise TypeError(
                f"{self.__class__.__name__} can only be multiplied by an int"
            )

    def __bool__(self) -> bool:
        return any(v > 0 for _, v in self)

    def __iter__(self) -> Iterator[tuple[Resource, int]]:
        yield (Resource.ORE, self.ore)
        yield (Resource.CLAY, self.clay)
        yield (Resource.OBSIDIAN, self.obsidian)
        yield (Resource.GEODE, self.geode)

    def resource(self, resource: Resource) -> int:
        match resource:
            case Resource.ORE:
                return self.ore
            case Resource.CLAY:
                return self.clay
            case Resource.OBSIDIAN:
                return self.obsidian
            case Resource.GEODE:
                return self.geode

    def covers(self, cost: "ResourceSet") -> bool:
        return all(s >= c for (_, s), (_, c) in zip(self, cost))


@dataclass(frozen=True)
class Blueprint:
    number: int
    ore: ResourceSet
    clay: ResourceSet
    obsidian: ResourceSet
    geode: ResourceSet

    def __iter__(self) -> Iterator[tuple[Resource, ResourceSet]]:
        yield Resource.ORE, self.ore
        yield Resource.CLAY, self.clay
        yield Resource.OBSIDIAN, self.obsidian
        yield Resource.GEODE, self.geode

    def get_cost(self, robot_type: Resource) -> ResourceSet:
        return getattr(self, robot_type.name.lower())


@dataclass(frozen=True)
class FactoryState:
    blueprint: Blueprint
    resources: ResourceSet
    robots_built: ResourceSet
    being_built: ResourceSet = ResourceSet()

    def validate(self) -> "FactoryState":
        if not (
            self.resources.ore >= 0
            and self.resources.clay >= 0
            and self.resources.obsidian >= 0
            and self.resources.geode >= 0
        ):
            raise ValueError()
        return self

    def work(self, robot_type: Resource | ResourceSet | None) -> "FactoryState":
        if robot_type is None:
            pre_collection_resources = self.resources
            new_robots_built_value = self.robots_built
        else:
            if isinstance(robot_type, Resource):
                cost = self.blueprint.get_cost(robot_type)
            else:
                cost = sum(
                    (
                        self.blueprint.get_cost(r)
                        for r, n in robot_type
                        for _ in range(n)
                    ),
                    ResourceSet(),
                )
            pre_collection_resources = self.resources - cost
            new_robots_built_value = self.robots_built + robot_type
        return FactoryState(
            self.blueprint,
            pre_collection_resources + self.robots_built,
            new_robots_built_value,
            self.robots_built,
        )

    def branch(self, time_left: int) -> set[tuple["FactoryState", int]]:
        branches = {
            (
                self.gather(turns_to_save).build(resource).gather(1),
                time_left - turns_to_save - 1,
            )
            for resource in Resource
            if 0 <= (turns_to_save := self.turns_to_save(resource)) < time_left - 1
            and not self.has_enough(resource)
        }
        branches.add((self.gather(time_left), 0))
        return branches

    def turns_to_save(self, robot: Resource) -> int:
        """Return -1 if not possible to save to build robot."""
        cost = self.blueprint.get_cost(robot)
        if self.resources.covers(cost):
            return 0
        one_minute_resources = self.resources + self.robots_built
        if one_minute_resources.covers(cost):
            return 1
        future_rate = self.robots_built + self.being_built
        needed = cost - one_minute_resources
        try:
            total_turns = (
                max(
                    math.ceil(value / future_rate.resource(res)) if value > 0 else 0
                    for res, value in needed
                )
                + 1
            )
        except ZeroDivisionError:
            total_turns = -1
        return total_turns

    def build(self, robot: Resource) -> "FactoryState":
        if self.being_built:
            raise ValueError(
                f"Cannot build {robot} while already building {self.being_built}"
            )
        cost = self.blueprint.get_cost(robot)
        return FactoryState(
            blueprint=self.blueprint,
            resources=self.resources - cost,
            robots_built=self.robots_built,
            being_built=self.being_built + robot,
        )

    def gather(self, minutes: int = 1) -> "FactoryState":
        if minutes < 0:
            raise ValueError(f"minutes must be non-negative")
        if minutes == 0:
            return self
        one_minute = FactoryState(
            blueprint=self.blueprint,
            resources=self.resources + self.robots_built,
            robots_built=self.robots_built + self.being_built,
        )
        if minutes == 1:
            state = one_minute
        else:
            state = FactoryState(
                blueprint=one_minute.blueprint,
                resources=one_minute.resources
                + one_minute.robots_built * (minutes - 1),
                robots_built=one_minute.robots_built,
            )
        return state

    def heuristic(self, time_left: int) -> int:
        """
        0 + 1 + 2 + 3 = 6 = ((4 - 1) + 1) * (4 - 1) / 2
        """
        return (
            self.resources.geode
            + time_left * self.robots_built.geode
            + time_left * (time_left - 1) // 2
        )

    def able_to_build(self, resource: Resource) -> bool:
        cost = self.blueprint.get_cost(resource)
        return self.resources.covers(cost)

    def has_enough(self, robot_type: Resource) -> bool:
        if robot_type == Resource.GEODE:
            return False
        costs = (self.blueprint.get_cost(resource) for resource in Resource)
        type_robots_built = self.robots_built.resource(robot_type)
        return all(cost.resource(robot_type) <= type_robots_built for cost in costs)
