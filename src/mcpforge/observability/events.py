"""Structured execution lifecycle events."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class ExecutionEvent:
    """A redacted, structured execution event."""

    name: str
    timestamp: datetime
    operation_id: str | None = None
    method: str | None = None
    path: str | None = None
    status_code: int | None = None
    duration_ms: float | None = None
    details: dict[str, Any] | None = None

    @classmethod
    def create(
        cls,
        name: str,
        *,
        operation_id: str | None = None,
        method: str | None = None,
        path: str | None = None,
        status_code: int | None = None,
        duration_ms: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> "ExecutionEvent":
        """Create an event with a UTC timestamp."""

        return cls(
            name=name,
            timestamp=datetime.now(UTC),
            operation_id=operation_id,
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            details=details,
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialize the event into logging-safe primitive values."""

        return {
            "event": self.name,
            "timestamp": self.timestamp.isoformat(),
            "operation_id": self.operation_id,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "duration_ms": self.duration_ms,
            "details": self.details,
        }
