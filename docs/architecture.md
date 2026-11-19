# Architecture

MCPForge converts REST API specifications into secure Model Context Protocol
servers through a staged pipeline.

## Pipeline

```text
OpenAPI / Swagger / Manual YAML
              |
              v
       Source Loaders
              |
              v
    Format Detection and Parsing
              |
              v
     Normalized Domain Contract
              |
              v
       Filtering and Policies
              |
              v
       MCP Tool Generation
              |
              v
       MCP SDK Adapter Layer
              |
              v
    Security and Authentication
              |
              v
      Async HTTP Execution
              |
              v
        Upstream REST API
```

## Architectural boundaries

### `domain`

The domain package contains framework-independent Pydantic models:

- `ApiDocument`
- `Endpoint`
- `Parameter`
- `RequestBody`
- `ResponseDefinition`
- `JsonSchema`

It must not import Typer, Rich, HTTPX, PyYAML, or the MCP SDK.

### `config`

The configuration package loads and validates project configuration. It owns:

- YAML and JSON configuration loading
- Pydantic configuration models
- Configuration merging
- Environment-variable references
- Secret-reference validation

Literal credentials are rejected. Secrets are resolved only at runtime.

### `ingestion`

Ingestion reads local or remote specifications and converts them into the
normalized domain contract.

The parser layer never generates MCP tools and never executes HTTP operations.

### `filtering`

Filtering applies:

- Path allowlists and blocklists
- Tag allowlists and blocklists
- HTTP method filters
- Deprecated-operation rules
- Read/write/delete safety rules

Exclusions take precedence over inclusions. Write and delete operations are
disabled by default.

### `generation`

Generation converts normalized endpoints into transport-independent
`ToolDefinition` objects. It handles:

- Deterministic names
- Name collisions
- Descriptions
- Input JSON schemas
- Parameter locations
- Manual overrides

Generated tools do not execute requests themselves.

### `auth`

Authentication providers resolve credentials from environment variables at
request time. Supported mechanisms include:

- Bearer tokens
- API keys in headers or query parameters
- HTTP Basic authentication
- Static environment-backed headers

### `execution`

The execution engine:

1. Validates tool arguments.
2. Builds the URL and request payload.
3. Injects runtime authentication.
4. Applies safety and network policies.
5. Sends the request through a shared `httpx.AsyncClient`.
6. Retries transient failures.
7. Enforces response limits.
8. Returns normalized success or error data.

### `security`

Security is centralized to prevent accidental bypasses. It owns:

- Operation safety
- Host allowlists
- DNS resolution checks
- Private-network blocking
- SSRF protection
- Secret redaction

### `mcp`

Only the `mcp` package imports the official MCP SDK. This adapter boundary
protects the core system from SDK-specific API changes.

### `runtime`

Runtime composition wires configuration, ingestion, filtering, generation,
authentication, execution, logging, and MCP transport into one application.

### `observability`

Observability provides structured lifecycle events, redacted logs, and safe
diagnostic summaries.

### `cli`

The CLI is a thin orchestration layer. Commands should call application
services and render results; they should not contain parsing or execution logic.

## Dependency direction

```text
CLI
 |
 v
Runtime
 |
 +--> Ingestion ------+
 +--> Filtering ------+--> Domain
 +--> Generation ----+
 +--> Execution -----+
 +--> Security ------+
 +--> MCP Adapter ---+
```

The dependency direction must remain inward toward the domain contract.
