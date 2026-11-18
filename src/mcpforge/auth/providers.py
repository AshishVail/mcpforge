"""Environment-backed authentication providers."""

from abc import ABC, abstractmethod
from collections.abc import Mapping

from mcpforge.auth.models import ResolvedAuth
from mcpforge.config.models import (
    ApiKeyAuthConfig,
    BasicAuthConfig,
    BearerAuthConfig,
    NoAuthConfig,
    StaticHeadersAuthConfig,
)
from mcpforge.config.secrets import resolve_env


class AuthProvider(ABC):
    """Provider interface for runtime authentication resolution."""

    @abstractmethod
    def resolve(self) -> ResolvedAuth:
        """Resolve authentication material from the environment."""
        raise NotImplementedError


class NoAuthProvider(AuthProvider):
    def __init__(self, config: NoAuthConfig) -> None:
        self.config = config

    def resolve(self) -> ResolvedAuth:
        return ResolvedAuth()


class BearerAuthProvider(AuthProvider):
    def __init__(self, config: BearerAuthConfig) -> None:
        self.config = config

    def resolve(self) -> ResolvedAuth:
        return ResolvedAuth(
            headers={"Authorization": f"Bearer {resolve_env(self.config.token)}"}
        )


class ApiKeyAuthProvider(AuthProvider):
    def __init__(self, config: ApiKeyAuthConfig) -> None:
        self.config = config

    def resolve(self) -> ResolvedAuth:
        value = resolve_env(self.config.value)
        if self.config.location == "query":
            return ResolvedAuth(query={self.config.name: value})
        return ResolvedAuth(headers={self.config.name: value})


class BasicAuthProvider(AuthProvider):
    def __init__(self, config: BasicAuthConfig) -> None:
        self.config = config

    def resolve(self) -> ResolvedAuth:
        return ResolvedAuth(
            username=resolve_env(self.config.username),
            password=resolve_env(self.config.password),
        )


class StaticHeadersAuthProvider(AuthProvider):
    def __init__(self, config: StaticHeadersAuthConfig) -> None:
        self.config = config

    def resolve(self) -> ResolvedAuth:
        return ResolvedAuth(
            headers={
                name: resolve_env(reference)
                for name, reference in self.config.headers.items()
            }
        )
