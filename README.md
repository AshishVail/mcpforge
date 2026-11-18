# ⚒️ MCPForge

**Turn Any REST API Into an AI-Ready MCP Server — Automatically, Securely, and Without Boilerplate.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP SDK Compatible](https://img.shields.io/badge/MCP-SDK%20Compatible-6C5CE7)](https://modelcontextprotocol.io/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![HTTPX Async](https://img.shields.io/badge/HTTPX-Async-0E7490)](https://www.python-httpx.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-Ruff-D7FF64)](https://docs.astral.sh/ruff/)
[![Type Checked: mypy](https://img.shields.io/badge/type_checked-mypy-2A6DB0)](https://mypy-lang.org/)

MCPForge transforms existing REST APIs into secure, typed Model Context Protocol
(MCP) servers. It reads OpenAPI 3.x, Swagger 2.0, or a simple developer-friendly
YAML configuration, normalizes it into a strongly typed internal model, generates
predictable MCP tools, and exposes those tools through local `stdio` or remote
`streamable-http` transports.

Instead of maintaining handwritten wrappers, duplicating validation schemas,
managing authentication separately, and rebuilding transport boilerplate, teams
can generate an AI-ready API integration in less than 60 seconds. MCPForge keeps
the normalized domain model independent of MCP and HTTP libraries, making the
system easier to test, extend, and maintain.

---

## Table of Contents

- [The Problem vs. the MCPForge Solution](#the-problem-vs-the-mcpforge-solution)
- [Core Features](#core-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [60-Second Quickstart](#60-second-quickstart)
- [CLI Command Reference](#cli-command-reference)
- [Configuration and Manual API Specs](#configuration-and-manual-api-specs)
- [Connecting to AI Clients](#connecting-to-ai-clients)
- [Security Model and Guardrails](#security-model-and-guardrails)
- [Project Directory Structure](#project-directory-structure)
- [Development and Quality Checks](#development-and-quality-checks)
- [Roadmap](#roadmap)
- [License and Attribution](#license-and-attribution)

---

## The Problem vs. the MCPForge Solution

### Before MCPForge

AI assistants cannot directly and safely call most REST APIs without a purpose-built
MCP integration. Teams traditionally need to:

- Read the API specification manually.
- Write endpoint-specific Python functions.
- Reimplement path, query, header, cookie, and JSON body mapping.
- Maintain duplicate Pydantic request models.
- Generate tool descriptions and names manually.
- Resolve authentication and secret sources safely.
- Implement SSRF and private-network protections.
- Normalize upstream errors for large-language-model recovery.
- Add retries, timeouts, response limits, redirects, and transport lifecycle logic.
- Maintain compatibility as the MCP SDK evolves.
- Rebuild similar boilerplate for every API and endpoint.

One API can become dozens of wrapper modules and still fail to scale as the API
changes.

### With MCPForge

```text
API specification or manual YAML
             |
             v
       MCPForge ingest
             |
             v
     Normalized API model
             |
             v
 Typed, filtered MCP tools
             |
             v
 stdio or streamable-http server
             |
             v
  Secure AI-to-REST execution
```

MCPForge separates API parsing from MCP generation and HTTP execution:

```text
OpenAPI / Swagger / Manual YAML
              │
              ▼
     Parse + Normalize
              │
              ▼
    Filter + Safety Policy
              │
              ▼
      Generate MCP Tools
              │
              ▼
   Serve through MCP SDK
              │
              ▼
  Authenticate + Execute API
```

The result is a repeatable pipeline:

```text
mcpforge run ./openapi.yaml
```

That command can import the specification, validate the configuration and security
policy, generate deterministic tools, and launch a functioning MCP server with
no handwritten endpoint wrappers.

---

## Core Features

### Multi-Source API Ingestion

MCPForge accepts multiple API definition formats:

| Source | Supported Formats | Description |
|---|---|---|
| Local file | OpenAPI 3.0 JSON/YAML | Reads a specification from disk |
| Local file | OpenAPI 3.1 JSON/YAML | Supports modern JSON Schema features |
| Local file | Swagger 2.0 JSON/YAML | Converts Swagger operations into the normalized model |
| Remote URL | OpenAPI or Swagger | Downloads and validates a remote specification |
| Manual YAML | `mcpforge.yaml` | Describes APIs that lack an official specification |

The ingestion pipeline extracts:

- Base URLs and server definitions
- Paths and HTTP methods
- Operation identifiers
- Summaries and descriptions
- Tags
- Path parameters
- Query parameters
- Header and cookie parameters
- JSON request bodies
- Required and optional fields
- Response schemas
- Deprecated operations
- Operation metadata used by filtering and generation

### Decoupled Normalized Domain Model

Every parser emits the same Pydantic v2 model:

- `ApiDocument`
- `Endpoint`
- `Parameter`
- `RequestBody`
- `ResponseDefinition`
- `JsonSchema`
- `ToolDefinition`

Parsers never generate MCP tools directly. The core generator and execution engine
only receive normalized domain objects. This architectural boundary allows future
protocol adapters for GraphQL, gRPC, SOAP, or internal API registries without
rewriting HTTP execution, security, or CLI logic.

```text
OpenAPIParser ─┐
SwaggerParser ─┼──> ApiDocument ──> ToolGenerator
ManualParser ──┘
```

### Deterministic Tool Generation

MCPForge generates clean MCP-compatible tool names, for example:

| REST Operation | Generated Tool |
|---|---|
| `GET /users/{id}` | `get_user` |
| `POST /orders` | `create_order` |
| `GET /users/{id}/projects` | `get_user_projects` |
| `DELETE /sessions/{id}` | `delete_session` |

Tool generation provides:

- Deterministic `snake_case` names
- Stable collision suffixing
- Operation-ID-aware naming
- Path and HTTP-method fallback naming
- Manual name overrides
- Manual description overrides
- Strict JSON input schemas
- Required/optional field definitions
- Nested request body support
- Parameter-location metadata
- Deprecated endpoint filtering
- Collision and ambiguous-name reporting

### Enterprise Security by Default

Safe behavior is the default:

- `GET`, `HEAD`, and `OPTIONS` may be exposed for read operations.
- `POST`, `PUT`, and `PATCH` require explicit write enablement.
- `DELETE` requires explicit delete enablement.
- Private, loopback, and link-local addresses are blocked.
- DNS resolutions are checked before and where possible during connection.
- Redirect targets are subject to the same network policy.
- `allowed_hosts` can restrict requests to explicit hostnames.
- Literal credentials are rejected from project configuration.
- Secrets are resolved only when a request is executed.
- Authorization, API keys, cookies, and static headers are redacted recursively.

### Zero-Leak Authentication

MCPForge supports:

- Bearer tokens
- API keys in custom headers
- API keys in query parameters
- HTTP Basic authentication
- Custom static headers
- Environment-variable-only runtime resolution

Credentials are not included in:

- YAML specifications
- Tool descriptions
- MCP schemas
- Terminal logs
- Debug messages
- HTTP exception text
- Structured API errors
- AI-visible tool responses

### Resilient Async Execution

The execution engine uses:

- A shared, lifecycle-managed `httpx.AsyncClient`
- Configurable connect and read timeouts
- Optional transient retry policies
- Exponential backoff
- Configurable maximum attempts
- TLS verification controls
- Redirect handling
- JSON body construction
- Query, path, header, and cookie mapping
- Maximum response payload limits
- Structured HTTP and network errors

Examples of normalized failure categories include:

- `validation_error`
- `authentication_failed`
- `authorization_failed`
- `not_found`
- `rate_limited`
- `upstream_unavailable`
- `timeout`
- `network_error`
- `invalid_json`
- `response_too_large`
- `host_blocked`
- `retry_exhausted`

### Dual MCP Transports

MCPForge is designed for both local and remote usage:

- **stdio:** ideal for Claude Desktop, Cursor, Windsurf, and local VS Code MCP clients
- **streamable-http:** suitable for remote deployments and centrally managed MCP gateways

The MCP SDK remains isolated behind an adapter layer. The domain model, tool
generator, authentication providers, and HTTP execution engine never depend on
SDK-specific classes.

---

## System Architecture

```text
┌──────────────────────────────────────────────────────────────────────┐
│                          MCPForge Pipeline                           │
└──────────────────────────────────────────────────────────────────────┘

 OpenAPI 3.x ──┐
 Swagger 2.0 ──┼──> Source Loaders
 Manual YAML ──┘       │
                       v
 ┌─────────────────────────────────────────────────────────────────────┐
 │ Local / Remote Ingestion + Format Detection + Schema Normalization  │
 └─────────────────────────────────────────────────────────────────────┘
                       │
                       v
 ┌─────────────────────────────────────────────────────────────────────┐
 │                    Unified Pydantic Domain Model                    │
 │ ApiDocument -> Endpoint -> Parameter -> RequestBody -> Responses   │
 └─────────────────────────────────────────────────────────────────────┘
                       │
                       v
 ┌─────────────────────────────────────────────────────────────────────┐
 │ Filter + Deprecated + Tag + Path + Method + Safety Policies        │
 └─────────────────────────────────────────────────────────────────────┘
                       │
                       v
 ┌─────────────────────────────────────────────────────────────────────┐
 │ Tool Generation: Naming, Overrides, Collisions, Input JSON Schemas  │
 └─────────────────────────────────────────────────────────────────────┘
                       │
                       v
 ┌─────────────────────────────────────────────────────────────────────┐
 │ MCP SDK Adapter + Stdio or Streamable HTTP Transport               │
 └─────────────────────────────────────────────────────────────────────┘
                       │
                       v
 ┌─────────────────────────────────────────────────────────────────────┐
 │ Argument Mapping -> Authentication -> SSRF -> HTTP Retry / Limits  │
 └─────────────────────────────────────────────────────────────────────┘
                       │
                       v
                   Upstream REST API
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `domain` | Pure Pydantic contracts shared by all internal modules |
| `config` | YAML/JSON loading, merging, validation, and environment references |
| `ingestion` | Source loading, format detection, parsing, and normalization |
| `filtering` | Endpoint allowlists, blocklists, tags, methods, and deprecated handling |
| `generation` | Tool names, descriptions, JSON schemas, and collision resolution |
| `auth` | Environment-backed authentication providers and credential resolution |
| `execution` | HTTP request construction, retries, response parsing, and normalized errors |
| `security` | Operation safety, SSRF protection, host policy, validation, and redaction |
| `mcp` | MCP SDK adapter and both transport implementations |
| `runtime` | Dependency composition and shared application lifecycle |
| `observability` | Redacted structured logging and diagnostics |
| `cli` | Terminal commands, argument handling, and Rich output |

The dependency direction remains one-way:

```text
cli -> runtime -> generation/filtering/execution
                       |
                       v
config -> ingestion -> domain
security -----------------^
mcp ----------------------^
```

The `domain` package must not import Typer, Rich, HTTPX, PyYAML, or the MCP SDK.

---

## Installation

### Requirements

- Python 3.11 or newer
- An MCP-compatible client for local usage
- Network access to the upstream API, if remote API testing is required

### Install with pip

```bash
python -m pip install mcpforge
```

For an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install mcpforge
mcpforge --help
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install mcpforge
mcpforge --help
```

### Install with uv

```bash
uv tool install mcpforge
mcpforge --help
```

For a project environment:

```bash
uv venv
source .venv/bin/activate
uv pip install mcpforge
```

### Install from source

```bash
git clone https://github.com/AshishVail/mcpforge.git
cd mcpforge
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Verify the installation:

```bash
mcpforge --version
mcpforge --help
```

---

## 60-Second Quickstart

### 1. Create a project

```bash
mkdir inventory-api && cd inventory-api
mcpforge init
```

This creates a starter `mcpforge.yaml` and supporting environment template.

### 2. Add environment-backed secrets

```bash
cp .env.example .env
export MCPFORGE_API_TOKEN="replace-with-your-token"
```

Never paste a token directly into `mcpforge.yaml`.

### 3. Import an API specification

Remote URL:

```bash
mcpforge import https://api.example.com/openapi.json
```

Local file:

```bash
mcpforge import ./openapi.yaml
```

Swagger 2.0:

```bash
mcpforge import ./swagger.yaml --format swagger
```

Manual configuration:

```bash
mcpforge import ./mcpforge.yaml --format manual
```

### 4. Inspect the generated tools

```bash
mcpforge inspect
```

Example output:

```text
┌───────┬────────────────────────┬───────────────┬──────────────┐
│ Method│ Path                   │ Tool Name     │ Safety       │
├───────┼────────────────────────┼───────────────┼──────────────┤
│ GET   │ /users/{id}            │ get_user      │ read         │
│ GET   │ /users                 │ list_users    │ read         │
│ POST  │ /orders                │ create_order  │ write        │
└───────┴────────────────────────┴───────────────┴──────────────┘
```

### 5. Validate configuration and security

```bash
mcpforge validate
```

The validation pass checks:

- YAML/JSON syntax
- Pydantic configuration models
- Source availability
- Schema validity
- Authentication references
- Write/delete policy
- Deprecated operations
- Host and SSRF policy
- Tool-name collisions
- Required environment variables

### 6. Test upstream connectivity

```bash
mcpforge test
```

Expected output:

```text
✓ Configuration loaded
✓ Authentication resolved
✓ API host allowed
✓ Connectivity successful
✓ Upstream returned a valid response
```

### 7. Start a local MCP server

```bash
mcpforge serve --transport stdio
```

To start the remote HTTP transport:

```bash
mcpforge serve --transport streamable-http --host 127.0.0.1 --port 8080
```

Streamable HTTP endpoint:

```text
http://127.0.0.1:8080/mcp
```

### 8. Use the one-command workflow

```bash
mcpforge run ./openapi.yaml
```

With remote OpenAPI:

```bash
mcpforge run https://api.example.com/openapi.json --transport stdio
```

With HTTP transport:

```bash
mcpforge run ./openapi.yaml \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8080
```

---

## CLI Command Reference

### `mcpforge init`

Scaffold a new MCPForge project.

```bash
mcpforge init
mcpforge init ./my-api
mcpforge init --force
mcpforge init --with-example
```

| Option | Description |
|---|---|
| `PATH` | Target project directory |
| `--force` | Replace existing project files after confirmation |
| `--with-example` | Include an example OpenAPI and environment file |
| `--config-name TEXT` | Custom configuration filename |

Creates:

```text
my-api/
├── mcpforge.yaml
├── .env.example
└── examples/
    └── petstore.openapi.yaml
```

### `mcpforge import`

Load and normalize an API specification.

```bash
mcpforge import ./openapi.yaml
mcpforge import ./swagger.json --format swagger
mcpforge import https://api.example.com/openapi.json
mcpforge import ./manual.yaml --format manual --save
```

| Option | Description |
|---|---|
| `<source>` | Local path or remote URL |
| `--format [openapi|swagger|manual]` | Explicit source format |
| `--save / --no-save` | Persist normalized project metadata |
| `--base-url TEXT` | Override a specification's server URL |
| `--config PATH` | Use a specific project configuration |

### `mcpforge inspect`

Display discovered endpoints and generated tool names.

```bash
mcpforge inspect
mcpforge inspect --methods GET
mcpforge inspect --tag users
mcpforge inspect --include-deprecated
mcpforge inspect --format json
```

| Option | Description |
|---|---|
| `--methods TEXT` | Filter by comma-separated HTTP methods |
| `--tag TEXT` | Filter by operation tag |
| `--path TEXT` | Filter by path substring or pattern |
| `--include-deprecated` | Include deprecated operations |
| `--format [table|json]` | Select Rich table or JSON output |

### `mcpforge validate`

Validate configuration, specifications, schemas, auth references, and security policy.

```bash
mcpforge validate
mcpforge validate --strict
mcpforge validate --config ./config/mcpforge.yaml
mcpforge validate --source ./openapi.yaml
```

| Option | Description |
|---|---|
| `--strict` | Treat warnings as validation failures |
| `--config PATH` | Validate a specific configuration |
| `--source PATH_OR_URL` | Validate a specific API source |
| `--show-secrets` | Never available; secret values are intentionally not rendered |

### `mcpforge test`

Verify API connectivity and authentication.

```bash
mcpforge test
mcpforge test --operation get_users
mcpforge test --operation get_user --param id=123
mcpforge test --timeout 15
mcpforge test --dry-run
```

| Option | Description |
|---|---|
| `--operation TEXT` | Invoke a specific endpoint |
| `--param KEY=VALUE` | Supply endpoint test parameters |
| `--timeout FLOAT` | Override HTTP timeout |
| `--dry-run` | Resolve configuration and auth without sending the request |
| `--verbose` | Show redacted request diagnostics |

### `mcpforge serve`

Launch the MCP server.

```bash
mcpforge serve --transport stdio
mcpforge serve --transport streamable-http --host 127.0.0.1 --port 8080
mcpforge serve --config ./mcpforge.yaml --log-level debug
```

| Option | Description |
|---|---|
| `--transport [stdio|streamable-http]` | MCP transport |
| `--host TEXT` | HTTP bind host |
| `--port INTEGER` | HTTP listen port |
| `--config PATH` | Project configuration file |
| `--log-level [debug|info|warning|error]` | Redacted runtime log level |

### `mcpforge run`

Import, validate, generate, and serve in one command.

```bash
mcpforge run ./openapi.yaml
mcpforge run https://api.example.com/openapi.yaml --transport stdio
mcpforge run ./openapi.yaml --allow-write
mcpforge run ./openapi.yaml --allow-delete
mcpforge run ./openapi.yaml --transport streamable-http --port 8080
```

| Option | Description |
|---|---|
| `<source>` | API specification or manual configuration |
| `--transport [stdio|streamable-http]` | MCP transport |
| `--host TEXT` | HTTP bind host |
| `--port INTEGER` | HTTP listen port |
| `--allow-write` | Explicitly enable write operations |
| `--allow-delete` | Explicitly enable delete operations |
| `--include-deprecated` | Include deprecated endpoints |
| `--config PATH` | Project configuration file |

### Global behavior

Every command should fail closed if:

- Authentication secrets are missing.
- Configuration contains literal credentials.
- A source cannot be safely loaded.
- Host policy rules conflict with the source host.
- Write or delete operations are enabled without explicit intent.
- A private or loopback host is discovered.
- The resolved DNS answer is prohibited.
- A tool schema is ambiguous or invalid.

---

## Configuration and Manual API Specs

### Complete `mcpforge.yaml` example

```yaml
name: inventory-api

source:
  location: https://api.example.com/openapi.json
  format: openapi
  base_url: https://api.example.com
  timeout_seconds: 30.0

auth:
  type: bearer
  token:
    env: MCPFORGE_API_TOKEN
    required: true

filters:
  include_paths:
    - /users
    - /users/{id}
    - /orders
    - /orders/{id}
  exclude_paths:
    - /internal/*
    - /admin/*
  include_tags:
    - Inventory
    - Orders
  exclude_tags:
    - Internal
  methods:
    - GET
    - POST
  include_deprecated: false

security:
  allow_write_operations: true
  allow_delete_operations: false
  allowed_hosts:
    - api.example.com
  block_private_networks: true
  max_response_bytes: 5000000

http:
  timeout_seconds: 30.0
  verify_tls: true
  retry:
    max_attempts: 3
    backoff_seconds: 0.5
```

### Bearer authentication

```yaml
auth:
  type: bearer
  token:
    env: MCPFORGE_API_TOKEN
    required: true
```

Do not use:

```yaml
auth:
  type: bearer
  token: sk-live-hardcoded-secret
```

### API key in a header

```yaml
auth:
  type: api_key
  name: X-API-Key
  location: header
  value:
    env: MCPFORGE_API_KEY
    required: true
```

### API key in a query parameter

```yaml
auth:
  type: api_key
  name: api_key
  location: query
  value:
    env: MCPFORGE_API_KEY
    required: true
```

### Basic authentication

```yaml
auth:
  type: basic
  username:
    env: MCPFORGE_API_USERNAME
    required: true
  password:
    env: MCPFORGE_API_PASSWORD
    required: true
```

### Custom static headers

```yaml
auth:
  type: static_headers
  headers:
    X-Tenant-ID:
      env: MCPFORGE_TENANT_ID
      required: true
    X-Client-Version:
      env: MCPFORGE_CLIENT_VERSION
      required: false
      default: "1.0"
```

### Manual API specification

MCPForge supports manual YAML when no OpenAPI specification is available:

```yaml
name: Inventory API
version: "1.0.0"
base_url: https://api.example.com

endpoints:
  - operation_id: list_products
    method: GET
    path: /products
    summary: List products
    description: Returns a paginated product catalog.
    tags:
      - Inventory
    parameters:
      - name: limit
        location: query
        required: false
        description: Maximum number of products to return.
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 20
      - name: cursor
        location: query
        required: false
        schema:
          type: string
    responses:
      - status_code: 200
        content_type: application/json
        description: Product page
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object
            next_cursor:
              type: string
              nullable: true

  - operation_id: get_product
    method: GET
    path: /products/{product_id}
    tags:
      - Inventory
    parameters:
      - name: product_id
        location: path
        required: true
        description: Product identifier.
        schema:
          type: string
    responses:
      - status_code: 200
        content_type: application/json
        description: Product found
      - status_code: 404
        description: Product not found
```

Manual request bodies use a JSON Schema-like structure:

```yaml
  - operation_id: create_product
    method: POST
    path: /products
    tags:
      - Inventory
    request_body:
      required: true
      content_type: application/json
      schema:
        type: object
        required:
          - name
          - price
        properties:
          name:
            type: string
            min_length: 1
          price:
            type: number
            minimum: 0
          category:
            type: string
            enum:
              - physical
              - digital
```

### Tool override example

```yaml
tool_overrides:
  get_product:
    name: fetch_inventory_product
    description: Fetch a product by its unique inventory identifier.
  delete_product:
    enabled: false
```

Tool overrides must not contain credentials or expose secret values.

---

## Connecting to AI Clients

Set secrets in the environment that launches your MCP client process.

```bash
export MCPFORGE_API_TOKEN="your-token"
```

### Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcpforge": {
      "command": "mcpforge",
      "args": [
        "serve",
        "--transport",
        "stdio",
        "--config",
        "/absolute/path/to/mcpforge.yaml"
      ],
      "env": {
        "MCPFORGE_API_TOKEN": "not-recommended-to-place-a-token-here"
      }
    }
  }
}
```

Prefer resolving secrets through Claude Desktop's environment or a system-level
secret manager. MCPForge can read `MCPFORGE_API_TOKEN` directly from the process
environment.

Claude Desktop locations:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: varies by MCP host configuration

### Cursor IDE

Create or update `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcpforge": {
      "command": "mcpforge",
      "args": [
        "serve",
        "--transport",
        "stdio",
        "--config",
        "${workspaceFolder}/mcpforge.yaml"
      ],
      "env": {
        "MCPFORGE_API_TOKEN": "${env:MCPFORGE_API_TOKEN}"
      }
    }
  }
}
```

### VS Code

VS Code MCP configurations commonly use a `.vscode/mcp.json` file:

```json
{
  "servers": {
    "mcpforge": {
      "type": "stdio",
      "command": "mcpforge",
      "args": [
        "serve",
        "--transport",
        "stdio",
        "--config",
        "${workspaceFolder}/mcpforge.yaml"
      ],
      "env": {
        "MCPFORGE_API_TOKEN": "${env:MCPFORGE_API_TOKEN}"
      }
    }
  }
}
```

Use the MCP configuration interface in VS Code if your installed version supports
workspace variable substitution or environment expansion.

### Windsurf

Add a project or user MCP configuration in the Windsurf MCP settings:

```json
{
  "mcpServers": {
    "mcpforge": {
      "command": "mcpforge",
      "args": [
        "serve",
        "--transport",
        "stdio",
        "--config",
        "/absolute/path/to/mcpforge.yaml"
      ],
      "env": {
        "MCPFORGE_API_TOKEN": "${env:MCPFORGE_API_TOKEN}"
      }
    }
  }
}
```

Use an absolute configuration path if the MCP host process does not inherit the
project working directory.

### Streamable HTTP Remote Server

Start the server:

```bash
MCPFORGE_API_TOKEN="your-token" \
mcpforge serve \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8080 \
  --config /srv/mcpforge/mcpforge.yaml
```

Configure a compatible MCP client:

```json
{
  "mcpServers": {
    "inventory-api": {
      "transport": "streamable-http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_GATEWAY_TOKEN}"
      }
    }
  }
}
```

Production deployments should place MCPForge behind:

- TLS termination
- Authentication
- Authorization
- Rate limiting
- Restricted network routing
- Health monitoring
- Centralized secret management

---

## Security Model and Guardrails

| Threat or Failure | MCPForge Protection |
|---|---|
| Accidental deletion | `DELETE` operations remain disabled unless explicitly enabled |
| Accidental writes | `POST`, `PUT`, and `PATCH` remain disabled unless configured |
| SSRF to loopback | Loopback addresses such as `127.0.0.0/8` and `::1` are blocked |
| SSRF to private networks | RFC1918 and equivalent private ranges are blocked by default |
| Link-local access | Link-local IPv4/IPv6 ranges are blocked |
| DNS rebinding | Resolved addresses are checked before execution and redirects |
| Host allowlist bypass | Requests outside `allowed_hosts` are rejected |
| Literal credentials | Configuration rejects credentials that are not environment references |
| Logs exposing secrets | Recursive redaction removes tokens and authorization values |
| MCP schema leakage | Credentials never become tool arguments or descriptions |
| Context overflow | Maximum response bytes are enforced before AI delivery |
| Invalid upstream JSON | Invalid JSON becomes a structured, recoverable error |
| Token rotation | Secrets resolve at runtime instead of during import or generation |
| Unbounded retries | Retry attempts are capped and backoff is configurable |
| Slow upstream API | Connect and read timeouts prevent indefinite execution |
| Redirect escape | Redirect hosts remain subject to allowed-host and SSRF policy |
| TLS interception | TLS verification is enabled by default |
| Ambiguous tool names | Collision resolution produces deterministic names and warnings |

### Operation Safety

Endpoint methods map to coarse safety categories:

| Method | Default Safety |
|---|---|
| `GET` | Read; enabled by default |
| `HEAD` | Read; enabled by default |
| `OPTIONS` | Read; enabled by default |
| `POST` | Write; explicit opt-in |
| `PUT` | Write; explicit opt-in |
| `PATCH` | Write; explicit opt-in |
| `DELETE` | Delete; explicit opt-in |

A write-enabled project does not imply delete-enabled behavior. Both flags are
evaluated independently.

### SSRF Defense

Before creating an upstream request, MCPForge should validate:

1. The scheme is HTTP or HTTPS.
2. The URL host matches `allowed_hosts`, where configured.
3. The hostname can be resolved.
4. Every resolved address is outside blocked ranges.
5. Redirect targets pass the same checks.
6. The selected connection cannot escape the validated address policy.

Private address detection is broad enough to include loopback, private, reserved,
link-local, multicast, unspecified, carrier-grade NAT, and other special-purpose
address families where applicable.

### Secret Redaction

Redaction applies recursively to:

- Dictionaries
- Lists
- Nested error details
- Exception messages
- Header collections
- Query logging
- Diagnostic JSON
- Terminal output

Sensitive names include values associated with:

- `authorization`
- `cookie`
- `set-cookie`
- `token`
- `api_key`
- `api-key`
- `password`
- `secret`
- `client_secret`
- `access_key`
- `session`

Redacted values are replaced consistently rather than being returned to AI clients.

### Response Size Protection

Every successful and error response is checked against `max_response_bytes`.

A payload exceeding the limit should result in:

```json
{
  "ok": false,
  "error": {
    "category": "response_too_large",
    "message": "The upstream response exceeded the configured payload limit.",
    "status_code": 200,
    "retryable": false
  }
}
```

The raw oversized body must not be included in the response delivered to the AI.

---

## Project Directory Structure

```text
mcpforge/
├── pyproject.toml                 # Build, dependencies, scripts, and tool settings
├── README.md                      # Project documentation
├── LICENSE                        # MIT license
├── CHANGELOG.md                   # Release history
├── Makefile                       # Common development commands
├── .gitignore                     # Repository ignore rules
├── .pre-commit-config.yaml        # Pre-commit quality hooks
│
├── docs/
│   ├── architecture.md            # Architecture and extension points
│   ├── configuration.md           # Complete configuration reference
│   ├── security.md                # Security guarantees and deployment guidance
│   └── supported-specifications.md
│
├── examples/
│   ├── basic/
│   │   ├── mcpforge.yaml          # Basic project configuration
│   │   └── .env.example           # Environment variable template
│   └── openapi/
│       └── petstore.yaml          # Example OpenAPI specification
│
├── src/
│   └── mcpforge/
│       ├── __init__.py            # Package metadata and public exports
│       ├── __main__.py            # `python -m mcpforge` entry point
│
│       ├── cli/
│       │   ├── app.py             # Typer application
│       │   ├── context.py         # Shared CLI context
│       │   ├── output.py          # Rich terminal rendering
│       │   └── commands/
│       │       ├── init.py        # Project scaffolding
│       │       ├── import_spec.py # API import
│       │       ├── inspect.py     # Endpoint and tool inspection
│       │       ├── validate.py    # Static validation
│       │       ├── test.py        # Connectivity and auth testing
│       │       ├── serve.py       # MCP server startup
│       │       └── run.py         # One-command pipeline
│
│       ├── config/
│       │   ├── models.py          # Pydantic configuration models
│       │   ├── loader.py          # YAML/JSON loading
│       │   ├── merger.py          # Configuration precedence
│       │   └── secrets.py         # Environment-backed secret resolution
│
│       ├── domain/
│       │   ├── enums.py           # HTTP, parameter, auth, and safety enums
│       │   ├── models.py          # ApiDocument and endpoint contracts
│       │   ├── parameters.py      # Parameter helpers
│       │   ├── schemas.py         # JSON schema aliases
│       │   └── errors.py          # Domain exceptions
│
│       ├── ingestion/
│       │   ├── service.py         # Format selection and ingestion workflow
│       │   ├── source.py          # Source descriptors
│       │   ├── loaders/           # Local and remote loading
│       │   ├── parsers/           # OpenAPI, Swagger, and manual parsers
│       │   └── normalization/     # Parser-specific conversion helpers
│
│       ├── filtering/
│       │   ├── policies.py        # Read/write/delete and deprecation policies
│       │   ├── selectors.py       # Path, tag, and method selectors
│       │   └── evaluator.py       # Final endpoint inclusion decision
│
│       ├── generation/
│       │   ├── models.py          # Generated ToolDefinition contracts
│       │   ├── naming.py          # Deterministic snake_case naming
│       │   ├── descriptions.py    # Tool descriptions
│       │   ├── collisions.py      # Stable collision resolution
│       │   ├── input_schema.py    # AI-facing JSON input schemas
│       │   └── service.py         # Endpoint-to-tool generation
│
│       ├── auth/
│       │   ├── models.py          # Authentication contracts
│       │   ├── providers.py        # Bearer, API key, Basic, and static auth
│       │   ├── resolver.py         # Runtime auth resolution
│       │   └── redaction.py        # Auth-related secret scrubbing
│
│       ├── execution/
│       │   ├── engine.py          # Request orchestration
│       │   ├── client.py          # Shared AsyncClient lifecycle
│       │   ├── request_builder.py # Path/query/header/body construction
│       │   ├── retry.py           # Retry and backoff policy
│       │   ├── response.py        # Response parsing
│       │   ├── errors.py          # Structured HTTP failures
│       │   └── limits.py          # Payload-size enforcement
│
│       ├── security/
│       │   ├── safety.py          # Operation safety policy
│       │   ├── ssrf.py            # DNS and private-network validation
│       │   ├── hosts.py           # Allowed-host enforcement
│       │   ├── validation.py      # Cross-cutting security validation
│       │   └── redaction.py       # Recursive output/log redaction
│
│       ├── mcp/
│       │   ├── adapter.py         # Internal-tool to MCP-SDK adapter
│       │   ├── server.py          # MCP server creation
│       │   ├── tools.py           # Tool callbacks
│       │   ├── errors.py          # MCP-compatible errors
│       │   └── transports.py      # stdio and streamable-http
│
│       ├── runtime/
│       │   ├── application.py     # Dependency composition
│       │   ├── lifecycle.py       # Startup and graceful shutdown
│       │   └── dependencies.py    # Runtime dependency providers
│
│       └── observability/
│           ├── logging.py         # Redacted logging
│           ├── events.py          # Structured events
│           └── diagnostics.py     # Safe diagnostics
│
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── domain/
    │   ├── config/
    │   ├── ingestion/
    │   ├── filtering/
    │   ├── generation/
    │   ├── auth/
    │   ├── execution/
    │   ├── security/
    │   ├── mcp/
    │   └── runtime/
    ├── integration/
    │   ├── ingestion/
    │   ├── execution/
    │   └── server/
    ├── fixtures/
    │   ├── openapi/
    │   ├── swagger/
    │   ├── manual/
    │   └── responses/
    └── e2e/
```

---

## Development and Quality Checks

### Clone and install

```bash
git clone https://github.com/AshishVail/mcpforge.git
cd mcpforge
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

### Run unit and integration tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=mcpforge --cov-report=term-missing --cov-report=html
```

Run a focused test directory:

```bash
pytest tests/unit/generation
pytest tests/integration/execution
```

### Run Ruff

```bash
ruff check .
ruff format --check .
ruff format .
ruff check --fix .
```

### Run mypy

```bash
mypy src
```

Strict typing is recommended for all pull requests.

### Makefile targets

```bash
make install
make test
make lint
make typecheck
make format
make check
```

Expected `make check` sequence:

```text
ruff check .
mypy src
pytest
```

### Pre-commit hooks

```bash
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Pull request checklist

Before submitting a pull request:

- [ ] Changes are covered by focused tests
- [ ] Public models remain Pydantic v2-compatible
- [ ] Domain code remains framework-independent
- [ ] MCP SDK imports stay behind the adapter layer
- [ ] Secrets are environment-backed
- [ ] Logs and errors pass through redaction
- [ ] SSRF and host-policy behavior is preserved
- [ ] Write and delete operations remain opt-in
- [ ] Ruff and mypy pass
- [ ] Documentation reflects CLI behavior or configuration changes

---

## Roadmap

### Current Foundation

- [x] Project identity and package structure
- [x] Pydantic normalized domain model
- [x] Strict project configuration
- [x] Environment-variable secret references
- [x] Typer/Rich CLI foundation
- [ ] OpenAPI 3.0 and 3.1 ingestion
- [ ] Swagger 2.0 conversion
- [ ] Manual YAML ingestion
- [ ] Deterministic MCP tool generation
- [ ] Authentication providers
- [ ] SSRF and host protection
- [ ] Async HTTP execution
- [ ] stdio and streamable-http transports
- [ ] Complete CLI workflow
- [ ] Enterprise documentation and examples

### Near-Term

- OpenAPI specification caching
- Endpoint-level tool overrides
- JSON Schema composition support
- GraphQL or gRPC protocol adapters
- OAuth 2.0 device authorization
- OAuth 2.0 client credentials
- Interactive secret resolution
- Docker and Kubernetes examples
- OpenTelemetry-compatible tracing
- Structured audit events
- Secret-manager provider plugins
- MCP prompt and resource generation
- Response transformation templates
- Interactive local configuration UI

### Long-Term

- API registry integration
- Remote specification discovery
- Signed configuration packages
- Policy-as-code plugins
- Organization-wide host allowlists
- Central credential brokers
- Automated schema drift detection
- Built-in API mock server
- Multi-API MCP gateway
- Per-user authorization mapping
- Enterprise audit and observability exports
- Compliance reporting
- Plugin marketplace for parsers and transports

---

## License and Attribution

MCPForge is licensed under the [MIT License](LICENSE).

Copyright 2026 [AshishVail](https://github.com/AshishVail).

MCPForge is independently maintained and is not affiliated with Anthropic,
Claude, Cursor, Microsoft, Windsurf, or the maintainers of the official MCP SDK.
All trademarks belong to their respective owners.

If MCPForge helps automate API integration for your team or project, consider:

- Starring the repository
- Reporting bugs and security issues
- Adding supported specifications
- Improving documentation
- Contributing parsers, auth providers, or MCP integrations
- Sharing your deployment architecture
