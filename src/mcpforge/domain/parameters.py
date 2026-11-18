"""Utilities for normalized endpoint parameters."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from mcpforge.domain.enums import ParameterLocation
from mcpforge.domain.models import Parameter


@dataclass(frozen=True, slots=True)
class ParameterCollection:
    """Immutable indexed view over endpoint parameters."""

    items: tuple[Parameter, ...]

    @classmethod
    def from_iterable(cls, parameters: Iterable[Parameter]) -> "ParameterCollection":
        return cls(tuple(parameters))

    def __iter__(self) -> Iterator[Parameter]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def by_location(self, location: ParameterLocation) -> tuple[Parameter, ...]:
        return tuple(parameter for parameter in self.items if parameter.location is location)

    def required(self) -> tuple[Parameter, ...]:
        return tuple(parameter for parameter in self.items if parameter.required)

    def names(self) -> frozenset[str]:
        return frozenset(parameter.name for parameter in self.items)
