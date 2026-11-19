# ⚒️ MCPForge

**Turn Any REST API Into an AI-Ready MCP Server — Automatically, Securely, and Without Boilerplate.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP SDK Compatible](https://img.shields.io/badge/MCP-SDK%20Compatible-6C5CE7)](https://modelcontextprotocol.io/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![HTTPX Async](https://img.shields.io/badge/HTTPX-Async-0E7490)](https://www.python-httpx.org/)
[![PyPI](https://img.shields.io/pypi/v/openapi-mcpforge?logo=pypi&logoColor=white)](https://pypi.org/project/openapi-mcpforge/)
[![GitHub Release](https://img.shields.io/github/v/release/AshishVail/mcpforge?logo=github)](https://github.com/AshishVail/mcpforge/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-Ruff-D7FF64)](https://docs.astral.sh/ruff/)
[![Type Checked: mypy](https://img.shields.io/badge/type_checked-mypy-2A6DB0)](https://mypy-lang.org/)
[![CI](https://github.com/AshishVail/mcpforge/actions/workflows/ci.yml/badge.svg)](https://github.com/AshishVail/mcpforge/actions/workflows/ci.yml)

> **Repository:** [github.com/AshishVail/mcpforge](https://github.com/AshishVail/mcpforge)  
> **PyPI package:** [openapi-mcpforge](https://pypi.org/project/openapi-mcpforge/)  
> **CLI command:** `mcpforge`  
> **Current release:** `v0.1.0`  
> **Maintainer:** [AshishVail](https://github.com/AshishVail)

MCPForge converts existing REST APIs into secure, typed Model Context Protocol
(MCP) servers. It accepts OpenAPI 3.0/3.1, Swagger 2.0, or a developer-friendly
manual YAML definition, normalizes the source into a strongly typed internal
contract, generates deterministic MCP tools, resolves authentication at
runtime, and exposes the result over local `stdio` or remote
`streamable-http` transports.

AI assistants should not require every developer to hand-write repetitive API
wrappers, request schemas, authentication logic, retry behavior, error
normalization, and transport boilerplate. MCPForge provides a production-minded
pipeline that makes REST APIs discoverable to AI clients while preserving
important safety controls: read-only defaults, explicit mutation permissions,
SSRF and DNS protection, host allowlists, environment-only secrets, recursive
redaction, bounded retries, timeouts, and response-size limits.

## Package Naming

The GitHub repository is named `mcpforge`, but the published PyPI distribution
is named `openapi-mcpforge` because the shorter `mcpforge` name was unavailable
on PyPI.

Install the published package with:

~~~bash
python -m pip install openapi-mcpforge
~~~

The executable remains:

~~~bash
mcpforge --help
~~~

The Python import namespace remains:

~~~python
import mcpforge
~~~

## Table of Contents

- [Why MCPForge?](#why-mcpforge)
- [The Problem vs. the Solution](#the-problem-vs-the-solution)
- [Core Features](#core-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [60-Second Quickstart](#60-second-quickstart)
- [Live Verification and Release Proof](#live-verification-and-release-proof)
- [CLI Command Reference](#cli-command-reference)
- [Configuration Guide](#configuration-guide)
- [Manual API Specifications](#manual-api-specifications)
- [Connecting AI Clients](#connecting-ai-clients)
- [Security Model and Guardrails](#security-model-and-guardrails)
- [Project Directory Structure](#project-directory-structure)
- [Development and Quality Checks](#development-and-quality-checks)
- [Troubleshooting and Common Gotchas](#troubleshooting-and-common-gotchas)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License and Attribution](#license-and-attribution)

---

## Why MCPForge?

REST APIs are ubiquitous, but AI assistants need structured, discoverable tools
rather than raw HTTP documentation. MCPForge bridges that gap by converting an
API contract into typed, policy-controlled MCP tools.

MCPForge is useful when you want to:

- Connect Claude Desktop, Cursor, Windsurf, or VS Code to an existing REST API.
- Avoid writing one-off MCP wrappers for every endpoint.
- Keep generated tools synchronized with OpenAPI or Swagger definitions.
- Expose only approved endpoints to an AI model.
- Resolve API credentials dynamically without placing secrets in configuration.
- Run locally over `stdio` or deploy remotely over `streamable-http`.
- Normalize upstream failures into responses an AI system can understand.
- Preserve a clean architecture that can support future protocol adapters.

---

## The Problem vs. the Solution

### Without MCPForge

A manually maintained integration typically requires:

- Reading the API specification.
- Writing one wrapper function per endpoint.
- Mapping path, query, header, cookie, and body values.
- Recreating Pydantic or JSON request models.
- Writing tool descriptions and names.
- Handling authentication and token rotation.
- Implementing retries, timeouts, and response limits.
- Normalizing HTTP errors for AI recovery.
- Protecting against SSRF and unsafe network targets.
- Redacting secrets from logs and diagnostics.
- Maintaining MCP SDK compatibility.
- Updating the wrapper whenever the API changes.

A moderately sized API can produce dozens or hundreds of repetitive wrapper
functions.

### With MCPForge

~~~text
OpenAPI / Swagger / Manual YAML
              |
              v
       Load and normalize
              |
              v
     Apply filters and policies
              |
              v
      Generate typed MCP tools
              |
              v
       Start an MCP server
              |
              v
 Securely execute upstream REST calls
~~~

Typical one-command workflow:

~~~bash
mcpforge run ./openapi.yaml
~~~

The pipeline is intentionally separated:

~~~text
Input Specification
        |
        v
Ingestion and Normalization
        |
        v
Filtering and Safety Policies
        |
        v
Deterministic Tool Generation
        |
        v
MCP Adapter and Transport
        |
        v
Authentication, SSRF Checks, and HTTP Execution
        |
        v
Upstream REST API
~~~

---

## Core Features

### Multi-Source API Ingestion

Supported sources include:

| Source | Formats |
|---|---|
| Local file | OpenAPI 3.0 JSON/YAML |
| Local file | OpenAPI 3.1 JSON/YAML |
| Local file | Swagger 2.0 JSON/YAML |
| Remote URL | OpenAPI or Swagger over HTTP(S) |
| Manual definition | MCPForge YAML |

The ingestion layer extracts:

- API title and version
- Base URL and server information
- Paths and HTTP methods
- Operation IDs
- Summaries and descriptions
- Tags
- Path parameters
- Query parameters
- Header parameters
- Cookie parameters
- JSON request bodies
- Required and optional fields
- Response status codes
- Response schemas
- Deprecated operations
- Local `$ref` schemas

### Decoupled Normalized Domain Model

All parsers emit the same Pydantic v2 internal model. Parsers never generate
MCP tools directly.

Core contracts include:

- `ApiDocument`
- `Endpoint`
- `Parameter`
- `RequestBody`
- `ResponseDefinition`
- `JsonSchema`
- `ToolDefinition`

This makes the system extensible. Future GraphQL, gRPC, or internal registry
adapters can target the same normalized model without rewriting generation,
security, or execution layers.

~~~text
OpenAPIParser ─┐
SwaggerParser ─┼──> ApiDocument ──> ToolGenerator
ManualParser ──┘
~~~

### Deterministic Tool Generation

MCPForge generates predictable `snake_case` names:

| REST Endpoint | Generated Tool |
|---|---|
| `GET /users` | `list_user` |
| `GET /users/{id}` | `get_user` |
| `POST /orders` | `create_order` |
| `PATCH /orders/{id}` | `update_order` |
| `DELETE /sessions/{id}` | `delete_session` |

Generation supports:

- `operationId`-based naming
- HTTP method and path fallback naming
- Singular/plural resource normalization
- Deterministic collision suffixes
- Manual name overrides
- Manual description overrides
- Strict JSON input schemas
- Required and optional fields
- Nested request bodies
- Parameter-location metadata
- Deprecated-operation filtering

### Enterprise Security by Default

MCPForge uses a fail-closed security model:

- `GET`, `HEAD`, and `OPTIONS` are read operations.
- `POST`, `PUT`, and `PATCH` require explicit write permission.
- `DELETE` requires separate explicit permission.
- Loopback, private, reserved, multicast, unspecified, and link-local
  destinations are blocked by default.
- DNS results are validated before network execution.
- Redirect destinations must satisfy the same host and network rules.
- `allowed_hosts` supports exact host enforcement.
- Literal credential values are rejected.
- Secrets are resolved only at runtime.
- Sensitive values are recursively redacted from logs and diagnostics.
- `max_response_bytes` prevents oversized upstream payloads from entering an
  AI context window.

### Runtime Authentication

Supported authentication methods:

- Bearer tokens
- API keys in headers
- API keys in query parameters
- HTTP Basic authentication
- Custom static headers

Secrets are referenced through environment variables:

~~~yaml
auth:
  type: bearer
  token:
    env: MCPFORGE_API_TOKEN
    required: true
~~~

The AI model receives tool metadata and schemas, never the underlying credential
values.

### Resilient Async Execution

The execution engine provides:

- Shared lifecycle-managed `httpx.AsyncClient`
- Configurable timeouts
- TLS verification
- Bounded retries
- Exponential backoff
- Path, query, header, cookie, and body mapping
- Structured HTTP errors
- Invalid JSON detection
- Request and response payload limits
- Redacted diagnostics
- Runtime authentication injection

### Dual MCP Transports

MCPForge supports:

- **`stdio`** for Claude Desktop, Cursor, Windsurf, and local VS Code usage.
- **`streamable-http`** for remote deployments and shared MCP gateways.

The official MCP SDK is isolated inside `src/mcpforge/mcp/`, protecting the
domain, ingestion, generation, and execution layers from SDK-specific changes.

---

## System Architecture

~~~text
┌──────────────────────────────────────────────────────────────────────────┐
│                              MCPForge                                    │
└──────────────────────────────────────────────────────────────────────────┘

 OpenAPI 3.0/3.1 ─┐
 Swagger 2.0      ├──> Local / Remote Source Loaders
 Manual YAML      ┘
                              |
                              v
                 Format Detection and Parsing
                              |
                              v
┌──────────────────────────────────────────────────────────────────────────┐
│                     Normalized Pydantic Domain Model                     │
│ ApiDocument -> Endpoint -> Parameter -> RequestBody -> Responses         │
└──────────────────────────────────────────────────────────────────────────┘
                              |
                              v
                 Filtering and Safety Policies
                              |
                              v
              Deterministic MCP Tool Generation
                              |
                              v
                   Official MCP SDK Adapter
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                 stdio          streamable-http
                    |                   |
                    +---------+---------+
                              |
                              v
     Argument Mapping -> Auth -> DNS/SSRF -> HTTPX -> Error Normalization
                              |
                              v
                       Upstream REST API
~~~

### Internal Modules

| Module | Responsibility |
|---|---|
| `domain` | Framework-independent Pydantic contracts |
| `config` | YAML/JSON configuration, merging, validation, and env references |
| `ingestion` | File/URL loading, format detection, parsing, and normalization |
| `filtering` | Path, tag, method, deprecation, and operation safety filters |
| `generation` | Tool names, descriptions, collisions, and input schemas |
| `auth` | Runtime environment-backed authentication providers |
| `execution` | Async HTTP requests, retries, limits, and error normalization |
| `security` | Safety, host policy, DNS checks, SSRF defense, and redaction |
| `mcp` | Official MCP SDK adapter and transports |
| `runtime` | Dependency composition and resource lifecycle |
| `observability` | Structured events, redacted logs, and diagnostics |
| `cli` | Typer commands and Rich terminal output |

### Dependency Direction

~~~text
cli
 |
 v
runtime
 |
 +--> ingestion ------+
 +--> filtering ------+--> domain
 +--> generation ----+
 +--> execution -----+
 +--> security ------+
 +--> mcp adapter ---+
~~~

The `domain` package remains independent of Typer, Rich, HTTPX, PyYAML, and the
MCP SDK. Only the MCP adapter imports the official MCP SDK.

---

## Installation

### Install the published PyPI package

~~~bash
python -m pip install openapi-mcpforge
~~~

Verify the CLI:

~~~bash
mcpforge --version
mcpforge --help
~~~

### Install with `uv`

~~~bash
uv tool install openapi-mcpforge
mcpforge --help
~~~

For a project environment:

~~~bash
uv venv
source .venv/bin/activate
uv pip install openapi-mcpforge
~~~

### Install from GitHub source

~~~bash
git clone https://github.com/AshishVail/mcpforge.git
cd mcpforge
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
~~~

### Install the `v0.1.0` source release

~~~bash
git clone --branch v0.1.0 https://github.com/AshishVail/mcpforge.git
cd mcpforge
python -m pip install -e ".[dev]"
~~~

---

## 60-Second Quickstart

### 1. Create a project

~~~bash
mkdir inventory-api
cd inventory-api
mcpforge init
~~~

### 2. Import an API specification

~~~bash
mcpforge import https://api.example.com/openapi.json
~~~

Or use a local file:

~~~bash
mcpforge import ./openapi.yaml
~~~

### 3. Inspect generated tools

~~~bash
mcpforge inspect
~~~

Example:

~~~text
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Method ┃ Path             ┃ Tool         ┃ Safety ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│ GET    │ /users           │ list_user    │ read   │
│ GET    │ /users/{id}      │ get_user     │ read   │
└────────┴──────────────────┴──────────────┴────────┘
~~~

### 4. Validate configuration and policies

~~~bash
mcpforge validate
~~~

### 5. Test connectivity

~~~bash
mcpforge test
~~~

### 6. Start a local MCP server

~~~bash
mcpforge serve --transport stdio
~~~

### 7. Start a remote server

~~~bash
mcpforge serve \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8080
~~~

### One-command workflow

~~~bash
mcpforge run ./openapi.yaml
~~~

---

## Live Verification and Release Proof

MCPForge `v0.1.0` has been released on GitHub and the project quality gates are
configured and verified for:

- Ruff linting
- Ruff formatting checks
- Strict mypy type checking
- pytest unit and integration tests
- Python 3.11 and 3.12 CI coverage

Release links:

- [GitHub Release v0.1.0](https://github.com/AshishVail/mcpforge/releases/tag/v0.1.0)
- [PyPI: openapi-mcpforge](https://pypi.org/project/openapi-mcpforge/)

### Install from PyPI

~~~bash
python -m pip install openapi-mcpforge
mcpforge --help
~~~

### Live JSONPlaceholder test

The live connectivity workflow requires an explicit `source.base_url`. The
specification describes the operation path, while `source.base_url` identifies
the actual upstream API origin.

Example configuration:

~~~yaml
name: jsonplaceholder

source:
  location: ./jsonplaceholder.yaml
  format: manual
  base_url: https://jsonplaceholder.typicode.com

auth:
  type: none

filters:
  methods:
    - GET

security:
  allow_write_operations: false
  allow_delete_operations: false
  allowed_hosts:
    - jsonplaceholder.typicode.com
  block_private_networks: true
  max_response_bytes: 5000000

http:
  timeout_seconds: 30
  verify_tls: true
  retry:
    max_attempts: 3
    backoff_seconds: 0.5
~~~

Manual operation:

~~~yaml
name: JSONPlaceholder API
version: "1.0.0"
base_url: https://jsonplaceholder.typicode.com

endpoints:
  - operation_id: get_todo
    method: GET
    path: /todos/1
    summary: Get todo 1
    responses:
      - status_code: 200
        description: Todo object
~~~

Run the live test:

~~~bash
mcpforge test \
  --config ./mcpforge.yaml \
  --operation get_todo
~~~

Expected output:

~~~text
✓ Connectivity successful: status 200
~~~

This verifies the complete path:

~~~text
Configuration
    -> Manual specification ingestion
    -> Endpoint filtering
    -> Tool/endpoint selection
    -> Base URL resolution
    -> Host and SSRF checks
    -> HTTPX request
    -> Live JSON response
    -> Normalized success result
~~~

Live tests should be used responsibly. Public APIs may change, rate-limit
requests, or impose their own terms of use.

---

## CLI Command Reference

### `mcpforge init`

Create a starter project:

~~~bash
mcpforge init
mcpforge init ./my-api
mcpforge init ./my-api --with-example
mcpforge init ./my-api --without-example
mcpforge init ./my-api --force
~~~

Options:

| Option | Description |
|---|---|
| `PATH` | Target project directory |
| `--force` | Overwrite generated files |
| `--with-example` | Include an example specification |
| `--without-example` | Omit the example specification |

### `mcpforge import`

Load and normalize a specification:

~~~bash
mcpforge import ./openapi.yaml
mcpforge import ./swagger.yaml --format swagger
mcpforge import ./mcpforge.yaml --format manual
mcpforge import https://api.example.com/openapi.json
~~~

Options:

| Option | Description |
|---|---|
| `SOURCE` | Local path or HTTP(S) URL |
| `--format` | `openapi`, `swagger`, or `manual` |
| `--timeout` | Remote source timeout in seconds |

### `mcpforge inspect`

Display generated tools:

~~~bash
mcpforge inspect
mcpforge inspect --config ./mcpforge.yaml
mcpforge inspect --format table
mcpforge inspect --format json
~~~

Options:

| Option | Description |
|---|---|
| `--config` | Project configuration path |
| `--format` | `table` or `json` |

### `mcpforge validate`

Validate configuration, ingestion, filtering, and generation:

~~~bash
mcpforge validate
mcpforge validate --config ./mcpforge.yaml
mcpforge validate --strict
~~~

Validation includes:

- Configuration syntax
- Pydantic model validation
- Source format detection
- Local reference resolution
- Endpoint safety
- Host allowlists
- Tool generation
- Authentication reference structure

### `mcpforge test`

Test upstream connectivity:

~~~bash
mcpforge test
mcpforge test --config ./mcpforge.yaml
mcpforge test --operation get_todo
mcpforge test --operation get_todo --dry-run
~~~

Options:

| Option | Description |
|---|---|
| `--config` | Project configuration path |
| `--operation` | Operation ID or endpoint path |
| `--dry-run` | Validate selection without sending a request |

### `mcpforge serve`

Start an MCP server:

~~~bash
mcpforge serve --transport stdio
mcpforge serve \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8080
~~~

Options:

| Option | Description |
|---|---|
| `--config` | Project configuration path |
| `--transport` | `stdio` or `streamable-http` |
| `--host` | HTTP bind host |
| `--port` | HTTP bind port |

### `mcpforge run`

Run the complete pipeline:

~~~bash
mcpforge run ./openapi.yaml
mcpforge run --config ./mcpforge.yaml
mcpforge run --transport stdio
mcpforge run \
  --config ./mcpforge.yaml \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8080
~~~

The command composes:

~~~text
Load configuration
    -> Ingest source
    -> Filter endpoints
    -> Generate tools
    -> Create MCP adapter
    -> Start selected transport
~~~

---

## Configuration Guide

MCPForge uses `mcpforge.yaml` or equivalent JSON.

### Minimal configuration

~~~yaml
source:
  location: ./openapi.yaml
~~~

The default behavior is intentionally conservative:

- Read operations are enabled.
- Write operations are disabled.
- Delete operations are disabled.
- Private-network access is blocked.
- TLS verification is enabled.
- Secrets must use environment-variable references.

### Complete configuration

~~~yaml
name: inventory-api

source:
  location: https://api.example.com/openapi.json
  format: openapi
  base_url: https://api.example.com
  timeout_seconds: 30

auth:
  type: bearer
  token:
    env: MCPFORGE_API_TOKEN
    required: true

filters:
  include_paths:
    - /users
    - /users/*
    - /orders
  exclude_paths:
    - /admin/*
    - /internal/*
  include_tags:
    - Public
    - Users
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
  timeout_seconds: 30
  verify_tls: true
  retry:
    max_attempts: 3
    backoff_seconds: 0.5
~~~

### Bearer authentication

~~~yaml
auth:
  type: bearer
  token:
    env: MCPFORGE_API_TOKEN
    required: true
~~~

### API key in a header

~~~yaml
auth:
  type: api_key
  name: X-API-Key
  location: header
  value:
    env: MCPFORGE_API_KEY
    required: true
~~~

### API key in a query parameter

~~~yaml
auth:
  type: api_key
  name: api_key
  location: query
  value:
    env: MCPFORGE_API_KEY
    required: true
~~~

### Basic authentication

~~~yaml
auth:
  type: basic
  username:
    env: MCPFORGE_API_USERNAME
    required: true
  password:
    env: MCPFORGE_API_PASSWORD
    required: true
~~~

### Static headers

~~~yaml
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
~~~

### Environment-only secrets

Valid:

~~~yaml
token:
  env: MCPFORGE_API_TOKEN
~~~

Invalid:

~~~yaml
token: "hardcoded-production-token"
~~~

The invalid form is rejected. Never commit real tokens to Git.

### Endpoint filters

~~~yaml
filters:
  include_paths:
    - /users
    - /users/*
  exclude_paths:
    - /admin/*
  include_tags:
    - Public
  exclude_tags:
    - Internal
  methods:
    - GET
  include_deprecated: false
~~~

Filtering precedence:

1. Excluded paths and tags always win.
2. Configured include paths act as an allowlist.
3. Configured include tags act as an allowlist.
4. Configured methods restrict the allowed methods.
5. Deprecated endpoints remain excluded unless enabled.
6. Operation safety policy is evaluated after selectors.

### Operation safety

~~~yaml
security:
  allow_write_operations: false
  allow_delete_operations: false
~~~

Enabling writes does not enable deletes:

~~~yaml
security:
  allow_write_operations: true
  allow_delete_operations: false
~~~

### Tool overrides

Tool override configuration can rename or describe generated tools:

~~~yaml
tool_overrides:
  get_user:
    name: fetch_user_profile
    description: Fetch a user profile by identifier.
  delete_user:
    enabled: false
~~~

Overrides must not contain credentials.

---

## Manual API Specifications

Manual YAML is useful when an API has no OpenAPI document.

~~~yaml
name: Inventory API
version: "1.0.0"
base_url: https://inventory.example.com

endpoints:
  - operation_id: list_items
    method: GET
    path: /items
    summary: List inventory items
    tags:
      - Inventory
    parameters:
      - name: limit
        location: query
        required: false
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 20
    responses:
      - status_code: 200
        description: Inventory items
        content_type: application/json
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object

  - operation_id: get_item
    method: GET
    path: /items/{item_id}
    summary: Get an inventory item
    parameters:
      - name: item_id
        location: path
        required: true
        schema:
          type: string
    responses:
      - status_code: 200
        description: Inventory item
      - status_code: 404
        description: Item not found
~~~

Manual request body:

~~~yaml
  - operation_id: create_item
    method: POST
    path: /items
    request_body:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
            properties:
              name:
                type: string
              price:
                type: number
                minimum: 0
    responses:
      - status_code: 201
        description: Item created
~~~

Manual specifications are converted into the same `ApiDocument` model used by
OpenAPI and Swagger.

---

## Connecting AI Clients

Set environment variables in the process environment used to launch the MCP
client:

~~~bash
export MCPFORGE_API_TOKEN="your-token"
~~~

Do not place production tokens directly into client configuration JSON.

### Claude Desktop

`claude_desktop_config.json`:

~~~json
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
        "MCPFORGE_API_TOKEN": "${MCPFORGE_API_TOKEN}"
      }
    }
  }
}
~~~

Typical locations:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: depends on the client installation

### Cursor

`.cursor/mcp.json`:

~~~json
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
~~~

### VS Code

`.vscode/mcp.json`:

~~~json
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
~~~

### Windsurf

Use the Windsurf MCP configuration:

~~~json
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
~~~

### Streamable HTTP

Start MCPForge:

~~~bash
MCPFORGE_API_TOKEN="$MCPFORGE_API_TOKEN" \
mcpforge serve \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8080 \
  --config /srv/mcpforge/mcpforge.yaml
~~~

A compatible client can connect to:

~~~text
https://mcp.example.com/mcp
~~~

Example remote configuration:

~~~json
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
~~~

For production, place the remote server behind TLS, authentication,
authorization, rate limiting, and restricted network access.

---

## Security Model and Guardrails

| Risk | Protection |
|---|---|
| Accidental deletion | `DELETE` disabled unless explicitly enabled |
| Accidental writes | `POST`, `PUT`, and `PATCH` require write permission |
| Loopback SSRF | Loopback IPv4/IPv6 destinations are blocked |
| Private-network SSRF | Private RFC1918 ranges are blocked |
| Link-local SSRF | Link-local addresses such as `169.254.0.0/16` are blocked |
| DNS rebinding | Resolved addresses are checked before execution |
| Redirect escape | Redirect targets must satisfy host and network policy |
| Host bypass | Exact `allowed_hosts` enforcement |
| Credential exposure | Secrets resolve only from environment variables |
| Log leakage | Recursive redaction of sensitive fields and known values |
| Context overflow | `max_response_bytes` limits upstream responses |
| Infinite retries | Retry attempts are capped |
| Slow upstream | Timeout settings bound request duration |
| Invalid upstream JSON | Converted into structured `invalid_json` errors |
| TLS interception | TLS verification is enabled by default |

### Safety defaults

| Method | Default |
|---|---|
| `GET` | Enabled |
| `HEAD` | Enabled |
| `OPTIONS` | Enabled |
| `POST` | Disabled |
| `PUT` | Disabled |
| `PATCH` | Disabled |
| `DELETE` | Disabled |

### SSRF and DNS validation

Before an upstream call, MCPForge validates:

1. The URL uses HTTP or HTTPS.
2. The URL includes a hostname.
3. The hostname passes `allowed_hosts`, when configured.
4. The hostname is not `localhost`.
5. DNS results do not resolve to blocked address ranges.
6. Redirect destinations remain subject to the same checks.
7. The request does not exceed configured payload limits.

### Secret redaction

Sensitive names include:

- `authorization`
- `proxy-authorization`
- `cookie`
- `set-cookie`
- `token`
- `password`
- `secret`
- `api_key`
- `access_token`
- `refresh_token`
- `client_secret`

Secrets are not placed into:

- Tool names
- Tool descriptions
- Input schemas
- MCP metadata
- Error payloads
- Diagnostic summaries
- Terminal logs

### Payload protection

Configure:

~~~yaml
security:
  max_response_bytes: 5000000
~~~

An oversized response is represented as a structured error rather than delivered
to the AI model.

### Deployment recommendations

For remote deployments:

- Use HTTPS.
- Place the server behind an authenticated gateway.
- Restrict inbound network access.
- Use a secret manager.
- Rotate credentials regularly.
- Enable audit logging.
- Apply external rate limiting.
- Run with a dedicated least-privilege service account.
- Keep MCP SDK and HTTP dependencies updated.
- Review endpoint allowlists before enabling writes or deletes.

MCPForge is a security layer, not a replacement for upstream API
authorization. The upstream API must still enforce identity, permissions,
tenant isolation, and business rules.

---

## Project Directory Structure

~~~text
mcpforge/
├── pyproject.toml                 # Build metadata and dependencies
├── README.md                      # Project documentation
├── LICENSE                        # MIT license
├── CHANGELOG.md                   # Release history
├── Makefile                       # Development shortcuts
├── .gitignore                     # Ignore rules
├── .pre-commit-config.yaml        # Formatting and type hooks
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # Python 3.11/3.12 quality gates
│
├── docs/
│   ├── architecture.md            # Architecture and boundaries
│   ├── configuration.md           # Configuration reference
│   ├── security.md                # Security model
│   └── supported-specifications.md
│
├── examples/
│   ├── basic/
│   │   ├── mcpforge.yaml          # Basic runtime configuration
│   │   └── .env.example           # Environment variable template
│   └── openapi/
│       └── petstore.yaml          # Example OpenAPI document
│
├── src/
│   └── mcpforge/
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── cli/
│       │   ├── app.py             # Typer root application
│       │   ├── context.py         # CLI state
│       │   ├── output.py          # Rich output
│       │   ├── scaffold.py        # Project scaffolding
│       │   └── commands/
│       │       ├── init.py
│       │       ├── import_spec.py
│       │       ├── inspect.py
│       │       ├── validate.py
│       │       ├── test.py
│       │       ├── serve.py
│       │       └── run.py
│       │
│       ├── config/
│       │   ├── models.py
│       │   ├── loader.py
│       │   ├── merger.py
│       │   └── secrets.py
│       │
│       ├── domain/
│       │   ├── enums.py
│       │   ├── models.py
│       │   ├── parameters.py
│       │   ├── schemas.py
│       │   └── errors.py
│       │
│       ├── ingestion/
│       │   ├── source.py
│       │   ├── service.py
│       │   ├── errors.py
│       │   ├── loaders/
│       │   ├── parsers/
│       │   └── normalization/
│       │
│       ├── filtering/
│       ├── generation/
│       ├── auth/
│       ├── execution/
│       ├── security/
│       ├── mcp/
│       ├── runtime/
│       └── observability/
│
└── tests/
    ├── conftest.py
    ├── fixtures/
    │   ├── openapi/
    │   ├── swagger/
    │   ├── manual/
    │   └── responses/
    ├── unit/
    │   ├── domain/
    │   ├── config/
    │   ├── ingestion/
    │   ├── filtering/
    │   ├── generation/
    │   ├── auth/
    │   ├── security/
    │   ├── execution/
    │   ├── mcp/
    │   ├── runtime/
    │   └── cli/
    ├── integration/
    │   ├── execution/
    │   ├── server/
    │   └── cli/
    └── e2e/
~~~

---

## Development and Quality Checks

### Install development dependencies

~~~bash
git clone https://github.com/AshishVail/mcpforge.git
cd mcpforge
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
~~~

### Run tests

~~~bash
python -m pytest
~~~

With coverage:

~~~bash
python -m pytest \
  --cov=mcpforge \
  --cov-report=term-missing \
  --cov-report=html
~~~

Run selected suites:

~~~bash
python -m pytest tests/unit
python -m pytest tests/integration
python -m pytest tests/e2e
~~~

### Ruff

~~~bash
python -m ruff check .
python -m ruff format --check .
~~~

Format locally:

~~~bash
python -m ruff format .
python -m ruff check --fix .
~~~

### mypy

~~~bash
python -m mypy src
~~~

The project uses strict type checking for production source code.

### Makefile

~~~bash
make install
make test
make lint
make typecheck
make format
make check
~~~

Recommended final check:

~~~bash
make check
~~~

### Pre-commit

~~~bash
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files
~~~

### CI

GitHub Actions runs on Python 3.11 and 3.12:

~~~text
Ruff lint
Ruff format check
mypy
pytest
~~~

Pull requests should keep all quality gates green.

---

## Troubleshooting and Common Gotchas

### `source.base_url` is missing during `mcpforge test`

The specification location is not necessarily the runtime API URL.

For example, this source:

~~~yaml
source:
  location: ./openapi.yaml
~~~

may describe paths without identifying the actual server. Add an explicit
`base_url`:

~~~yaml
source:
  location: ./openapi.yaml
  format: openapi
  base_url: https://api.example.com
~~~

For OpenAPI documents, `servers[0].url` may provide a base URL, but explicitly
setting `source.base_url` makes runtime behavior clear and reliable.

### PyPI package name collision

Install the published package using:

~~~bash
python -m pip install openapi-mcpforge
~~~

Run the CLI using:

~~~bash
mcpforge --help
~~~

Do not try to install `mcpforge` from PyPI. The repository remains:

~~~text
https://github.com/AshishVail/mcpforge
~~~

If a package upload returns HTTP `400` because a distribution name already
exists, verify that `pyproject.toml` uses:

~~~toml
[project]
name = "openapi-mcpforge"
~~~

### PyPI upload with 2FA and API tokens

For PyPI uploads, use an API token rather than a password:

~~~bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-your-token"
python -m build
python -m twine upload dist/*
~~~

The username must be exactly `__token__` when using a PyPI API token.

Never place the token in:

- `pyproject.toml`
- Shell scripts committed to Git
- GitHub workflow source
- README examples
- Issue comments
- Logs
- Source code

For GitHub Actions, store the token as an encrypted repository or environment
secret such as `PYPI_API_TOKEN`.

### Write operation is blocked

This is expected by default:

~~~text
write operation is disabled
~~~

Enable writes explicitly:

~~~yaml
security:
  allow_write_operations: true
~~~

This enables `POST`, `PUT`, and `PATCH`, but not `DELETE`.

### Delete operation is blocked

Enable delete operations independently:

~~~yaml
security:
  allow_delete_operations: true
~~~

Use this only after reviewing the endpoint allowlist and upstream API
authorization policy.

### Host is blocked or SSRF protection triggers

Check:

~~~yaml
security:
  allowed_hosts:
    - api.example.com
  block_private_networks: true
~~~

If the destination resolves to a private, loopback, link-local, reserved,
multicast, unspecified, or otherwise special address, the request is
intentionally rejected.

For public API testing, ensure the hostname is explicitly allowed when an
allowlist is configured:

~~~yaml
security:
  allowed_hosts:
    - jsonplaceholder.typicode.com
~~~

### Authentication environment variable is missing

For:

~~~yaml
auth:
  type: bearer
  token:
    env: MCPFORGE_API_TOKEN
    required: true
~~~

set:

~~~bash
export MCPFORGE_API_TOKEN="your-token"
~~~

Check only whether the variable exists; do not print its value:

~~~bash
test -n "$MCPFORGE_API_TOKEN" && echo "token configured"
~~~

### Response is too large

Increase the limit only when the AI client can safely handle the payload:

~~~yaml
security:
  max_response_bytes: 10000000
~~~

Prefer upstream pagination, filtering, or narrower endpoints instead of allowing
unbounded responses.

### Tool is not visible in the AI client

Check:

1. `mcpforge inspect`
2. `mcpforge validate`
3. The client configuration path
4. The `mcpforge` executable path
5. Environment-variable inheritance
6. The selected transport
7. Client logs
8. Whether the endpoint was filtered or blocked by safety policy

### MCP server starts but API calls fail

Run:

~~~bash
mcpforge test \
  --config ./mcpforge.yaml \
  --operation your_operation_id
~~~

Then verify:

- `source.base_url`
- `allowed_hosts`
- Environment-backed authentication
- TLS verification
- Endpoint path parameters
- Upstream API permissions
- Timeout and retry settings

### Ruff reports formatting or lint failures

Run:

~~~bash
python -m ruff format .
python -m ruff check --fix .
python -m ruff check .
~~~

The CI workflow treats Ruff lint and formatting failures as blocking errors.

### mypy reports type failures

Run:

~~~bash
python -m mypy src
~~~

Avoid weakening strict typing with broad `Any` values or unsafe casts. Prefer
explicit domain models, guards, and typed adapters.

---

## Roadmap

### Completed in `v0.1.0`

- [x] Repository architecture and package boundaries
- [x] Pydantic v2 normalized domain models
- [x] YAML and JSON configuration
- [x] Environment-only secret references
- [x] OpenAPI 3.0 ingestion
- [x] OpenAPI 3.1 ingestion
- [x] Swagger 2.0 ingestion
- [x] Manual YAML ingestion
- [x] Local and remote specification loading
- [x] Local JSON Pointer reference resolution
- [x] Deterministic MCP tool generation
- [x] Tool name collision handling
- [x] Path, tag, and method filtering
- [x] Read-only defaults
- [x] Explicit write and delete policies
- [x] Bearer authentication
- [x] Header and query API keys
- [x] Basic authentication
- [x] Static environment-backed headers
- [x] Recursive secret redaction
- [x] SSRF and private-network protection
- [x] DNS and host validation
- [x] Redirect and allowed-host enforcement
- [x] Async HTTP execution
- [x] Shared HTTP client lifecycle
- [x] Timeout and retry controls
- [x] Structured HTTP errors
- [x] Request and response-size limits
- [x] MCP SDK adapter layer
- [x] `stdio` transport
- [x] `streamable-http` transport
- [x] Complete CLI workflow
- [x] Ruff linting and formatting checks
- [x] Strict mypy checking
- [x] pytest unit and integration coverage
- [x] Python 3.11 and 3.12 CI
- [x] GitHub release `v0.1.0`
- [x] PyPI distribution `openapi-mcpforge`
- [x] Live upstream API verification against JSONPlaceholder

### Near-Term

- [ ] Improved OpenAPI composition support for `allOf`, `oneOf`, and `anyOf`
- [ ] Multipart and file-upload schema support
- [ ] Endpoint-level enable/disable overrides
- [ ] Advanced serialization styles and explode rules
- [ ] OAuth 2.0 device authorization
- [ ] OAuth 2.0 client credentials
- [ ] Secret-manager integrations
- [ ] Docker deployment examples
- [ ] Kubernetes deployment examples
- [ ] OpenTelemetry-compatible tracing
- [ ] Structured audit event exports
- [ ] API schema drift detection
- [ ] Response transformation templates
- [ ] MCP resources and prompts

### Long-Term

- [ ] GraphQL protocol adapter
- [ ] gRPC protocol adapter
- [ ] Multi-API MCP gateway
- [ ] API registry integration
- [ ] Signed configuration packages
- [ ] Organization-wide policy plugins
- [ ] Central credential brokers
- [ ] Per-user authorization mapping
- [ ] Built-in API mock server
- [ ] Compliance and audit reporting
- [ ] Extension marketplace for parsers and transports

---

## Contributing

Contributions are welcome.

Before opening a pull request:

- Keep the dependency direction intact.
- Keep `domain` framework-independent.
- Keep official MCP SDK imports inside `mcpforge.mcp`.
- Add focused tests for new behavior.
- Do not add credentials or sensitive fixtures.
- Preserve read/write/delete safety defaults.
- Preserve SSRF and host validation.
- Run `make check`.
- Update documentation for user-visible changes.
- Update `CHANGELOG.md` when appropriate.

Recommended workflow:

~~~bash
git checkout -b feature/my-change
python -m pip install -e ".[dev]"
make check
git commit -m "Add my change"
git push origin feature/my-change
~~~

---

## License and Attribution

MCPForge is released under the [MIT License](LICENSE).

Copyright 2026 [AshishVail](https://github.com/AshishVail).

- GitHub: [AshishVail/mcpforge](https://github.com/AshishVail/mcpforge)
- PyPI: [openapi-mcpforge](https://pypi.org/project/openapi-mcpforge/)
- Release: [v0.1.0](https://github.com/AshishVail/mcpforge/releases/tag/v0.1.0)

MCPForge is independently maintained and is not affiliated with Anthropic,
Claude, Cursor, Microsoft, Windsurf, or the maintainers of the official MCP
SDK. All trademarks belong to their respective owners.
