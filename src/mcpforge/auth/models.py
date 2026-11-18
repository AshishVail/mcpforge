"""Authentication request material contracts."""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ResolvedAuth:
    """Resolved request authentication material."""

    headers: Mapping[str, str] = field(default_factory=dict)
    query: Mapping[str, str] = field(default_factory=dict)
    username: str | None = None
    password: str | None = None

    def redacted(self) -> "ResolvedAuth":
        """Return a copy with all sensitive values masked."""

        mask = "***REDACTED***"
        return ResolvedAuth(
            headers={key: mask for key in self.headers},
            query={key: mask for key in self.query},
            username=mask if self.username is not None else None,
            password=mask if self.password is not None else None,
        )
