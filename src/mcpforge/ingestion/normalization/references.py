"""Local JSON Pointer reference resolution with cycle detection."""

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from mcpforge.ingestion.errors import ReferenceResolutionError


class ReferenceResolver:
    """Resolve local JSON references against one specification document."""

    def __init__(self, document: Mapping[str, Any]) -> None:
        self._document = document

    def resolve(self, value: Any, stack: tuple[str, ...] = ()) -> Any:
        """Resolve references recursively while preserving non-reference values."""

        if isinstance(value, list):
            return [self.resolve(item, stack) for item in value]

        if not isinstance(value, Mapping):
            return deepcopy(value)

        if "$ref" in value:
            reference = value["$ref"]
            if not isinstance(reference, str) or not reference.startswith("#/"):
                raise ReferenceResolutionError(
                    f"only local references are supported: {reference!r}"
                )
            if reference in stack:
                chain = " -> ".join((*stack, reference))
                raise ReferenceResolutionError(f"cyclic reference detected: {chain}")

            target = self._lookup(reference)
            resolved = self.resolve(target, (*stack, reference))

            siblings = {
                key: item
                for key, item in value.items()
                if key != "$ref"
            }
            if siblings and isinstance(resolved, Mapping):
                merged = dict(resolved)
                merged.update(
                    {
                        key: self.resolve(item, (*stack, reference))
                        for key, item in siblings.items()
                    }
                )
                return merged
            return resolved

        return {
            str(key): self.resolve(item, stack)
            for key, item in value.items()
        }

    def _lookup(self, reference: str) -> Any:
        current: Any = self._document
        for token in reference[2:].split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            if isinstance(current, Mapping) and token in current:
                current = current[token]
            else:
                raise ReferenceResolutionError(f"unresolved local reference: {reference}")
        return current
