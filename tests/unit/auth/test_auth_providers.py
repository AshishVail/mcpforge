from mcpforge.auth.providers import ApiKeyAuthProvider, BearerAuthProvider
from mcpforge.config.models import (
    ApiKeyAuthConfig,
    BearerAuthConfig,
    EnvReference,
)


def test_bearer_provider_resolves_environment(monkeypatch) -> None:
    monkeypatch.setenv("MCPFORGE_TOKEN", "token-value")
    provider = BearerAuthProvider(BearerAuthConfig(token=EnvReference(env="MCPFORGE_TOKEN")))

    assert provider.resolve().headers["Authorization"] == "Bearer token-value"


def test_api_key_query_provider(monkeypatch) -> None:
    monkeypatch.setenv("MCPFORGE_KEY", "key-value")
    provider = ApiKeyAuthProvider(
        ApiKeyAuthConfig(
            name="api_key",
            location="query",
            value=EnvReference(env="MCPFORGE_KEY"),
        )
    )

    assert provider.resolve().query["api_key"] == "key-value"
