"""Endpoint safety policies."""

from dataclasses import dataclass

from mcpforge.config.models import SecurityConfig
from mcpforge.domain.enums import HttpMethod, OperationSafety
from mcpforge.domain.models import Endpoint


@dataclass(frozen=True, slots=True)
class SafetyPolicy:
    """Controls which operation classes may be exposed."""

    allow_write_operations: bool = False
    allow_delete_operations: bool = False
    include_deprecated: bool = False

    @classmethod
    def from_config(
        cls, config: SecurityConfig, include_deprecated: bool = False
    ) -> "SafetyPolicy":
        return cls(
            allow_write_operations=config.allow_write_operations,
            allow_delete_operations=config.allow_delete_operations,
            include_deprecated=include_deprecated,
        )

    def allows(self, endpoint: Endpoint) -> bool:
        if endpoint.deprecated and not self.include_deprecated:
            return False
        safety = endpoint.safety or self.classify(endpoint.method)
        if safety is OperationSafety.DELETE:
            return self.allow_delete_operations
        if safety is OperationSafety.WRITE:
            return self.allow_write_operations
        return True

    @staticmethod
    def classify(method: HttpMethod) -> OperationSafety:
        if method is HttpMethod.DELETE:
            return OperationSafety.DELETE
        if method in {HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH}:
            return OperationSafety.WRITE
        return OperationSafety.READ
