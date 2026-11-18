"""Authentication provider selection."""

from mcpforge.auth.models import ResolvedAuth
from mcpforge.auth.providers import (
    ApiKeyAuthProvider,
    AuthProvider,
    BasicAuthProvider,
    BearerAuthProvider,
    NoAuthProvider,
    StaticHeadersAuthProvider,
)
from mcpforge.config.models import (
    ApiKeyAuthConfig,
    BasicAuthConfig,
    BearerAuthConfig,
    NoAuthConfig,
    ProjectConfig,
    StaticHeadersAuthConfig,
)


def provider_for(config: ProjectConfig) -> AuthProvider:
    """Create the provider matching project authentication configuration."""

    auth = config.auth
    if isinstance(auth, NoAuthConfig):
        return NoAuthProvider(auth)
    if isinstance(auth, BearerAuthConfig):
        return BearerAuthProvider(auth)
    if isinstance(auth, ApiKeyAuthConfig):
        return ApiKeyAuthProvider(auth)
    if isinstance(auth, BasicAuthConfig):
        return BasicAuthProvider(auth)
    if isinstance(auth, StaticHeadersAuthConfig):
        return StaticHeadersAuthProvider(auth)
    raise TypeError(f"unsupported authentication configuration: {type(auth).__name__}")


def resolve_auth(config: ProjectConfig) -> ResolvedAuth:
    """Resolve project authentication at request time."""

    return provider_for(config).resolve()
