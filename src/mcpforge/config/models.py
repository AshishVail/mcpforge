"""Strict user-facing MCPForge project configuration models."""

from typing import Annotated, Literal, Self

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator

from mcpforge.config.secrets import validate_secret_references
from mcpforge.domain.enums import AuthType, HttpMethod


class EnvReference(BaseModel):
    """Reference to a value resolved from an environment variable."""

    model_config = ConfigDict(extra="forbid")

    env: Annotated[
        str,
        Field(
            min_length=1,
            pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
        ),
    ]
    required: bool = True
    default: str | None = None

    @model_validator(mode="after")
    def validate_default(self) -> Self:
        if self.required and self.default is not None:
            raise ValueError("required environment references cannot define defaults")
        return self


class ApiSourceConfig(BaseModel):
    """API specification source configuration."""

    model_config = ConfigDict(extra="forbid")

    location: Annotated[str, Field(min_length=1)]
    format: Literal["openapi", "swagger", "manual"] | None = None
    base_url: AnyHttpUrl | None = None
    timeout_seconds: Annotated[float, Field(gt=0, le=300)] = 30.0


class NoAuthConfig(BaseModel):
    """Explicitly unauthenticated API configuration."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[AuthType.NONE] = AuthType.NONE


class BearerAuthConfig(BaseModel):
    """Bearer-token authentication configuration."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[AuthType.BEARER] = AuthType.BEARER
    token: EnvReference


class ApiKeyAuthConfig(BaseModel):
    """API-key authentication configuration."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[AuthType.API_KEY] = AuthType.API_KEY
    name: Annotated[str, Field(min_length=1)]
    location: Literal["header", "query"] = "header"
    value: EnvReference


class BasicAuthConfig(BaseModel):
    """HTTP Basic authentication configuration."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[AuthType.BASIC] = AuthType.BASIC
    username: EnvReference
    password: EnvReference


class StaticHeadersAuthConfig(BaseModel):
    """Environment-backed static header configuration."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[AuthType.STATIC_HEADERS] = AuthType.STATIC_HEADERS
    headers: dict[
        Annotated[str, Field(min_length=1)],
        EnvReference,
    ] = Field(min_length=1)


AuthConfig = (
    NoAuthConfig | BearerAuthConfig | ApiKeyAuthConfig | BasicAuthConfig | StaticHeadersAuthConfig
)


class EndpointFilterConfig(BaseModel):
    """Endpoint inclusion and exclusion rules."""

    model_config = ConfigDict(extra="forbid")

    include_paths: list[str] = Field(default_factory=list)
    exclude_paths: list[str] = Field(default_factory=list)
    include_tags: list[str] = Field(default_factory=list)
    exclude_tags: list[str] = Field(default_factory=list)
    methods: set[HttpMethod] | None = None
    include_deprecated: bool = False


class SecurityConfig(BaseModel):
    """Operation and network security controls."""

    model_config = ConfigDict(extra="forbid")

    allow_write_operations: bool = False
    allow_delete_operations: bool = False
    allowed_hosts: set[str] = Field(default_factory=set)
    block_private_networks: bool = True
    max_response_bytes: Annotated[int, Field(gt=0, le=100_000_000)] = 5_000_000


class RetryConfig(BaseModel):
    """Transient request retry policy."""

    model_config = ConfigDict(extra="forbid")

    max_attempts: Annotated[int, Field(ge=1, le=10)] = 3
    backoff_seconds: Annotated[float, Field(ge=0, le=60)] = 0.5


class HttpConfig(BaseModel):
    """HTTP client and retry settings."""

    model_config = ConfigDict(extra="forbid")

    timeout_seconds: Annotated[float, Field(gt=0, le=300)] = 30.0
    retry: RetryConfig = Field(default_factory=RetryConfig)
    verify_tls: bool = True


class ProjectConfig(BaseModel):
    """Top-level ``mcpforge.yaml`` project configuration."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str,
        Field(
            min_length=1,
            pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$",
        ),
    ] = "mcpforge-project"
    source: ApiSourceConfig
    auth: AuthConfig = Field(default_factory=NoAuthConfig)
    filters: EndpointFilterConfig = Field(default_factory=EndpointFilterConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    http: HttpConfig = Field(default_factory=HttpConfig)

    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        validate_secret_references(self.model_dump(mode="python"))

        if self.source.base_url is not None and self.security.allowed_hosts:
            source_host = self.source.base_url.host
            if source_host is None:
                raise ValueError("source base URL must include a host")
            allowed_hosts = {
                host.strip().rstrip(".").lower() for host in self.security.allowed_hosts
            }
            if source_host.lower().rstrip(".") not in allowed_hosts:
                raise ValueError(
                    f"source host {source_host!r} is not present in security.allowed_hosts"
                )

        return self

    def safe_dump(self) -> dict[str, object]:
        """Serialize configuration without resolving secret values."""

        return self.model_dump(mode="json")
