"""Safe recursive configuration merging."""

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


def merge_mappings(
    base: Mapping[str, Any],
    override: Mapping[str, Any],
) -> dict[str, Any]:
    """Deep-merge mappings without mutating either input.

    Nested mappings merge recursively. Lists and scalar values are replaced
    by the overriding value.
    """

    result: dict[str, Any] = deepcopy(dict(base))
    for key, value in override.items():
        current = result.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            result[key] = merge_mappings(current, value)
        else:
            result[key] = deepcopy(value)
    return result
