"""Deterministic generated-name collision handling."""

from collections.abc import Iterable

from mcpforge.domain.models import Endpoint
from mcpforge.generation.naming import default_tool_name


def unique_names(endpoints: Iterable[Endpoint]) -> dict[int, str]:
    """Assign stable unique names using operation order and numeric suffixes."""

    used: set[str] = set()
    result: dict[int, str] = {}

    for index, endpoint in enumerate(endpoints):
        base = default_tool_name(endpoint)
        name = base
        suffix = 2
        while name in used:
            name = f"{base}_{suffix}"
            suffix += 1
        used.add(name)
        result[index] = name
    return result
