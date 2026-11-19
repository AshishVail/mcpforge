# Configuration

MCPForge projects use `mcpforge.yaml` or JSON with equivalent fields.

## Minimal configuration

```yaml
source:
  location: ./openapi.yaml
```

The default behavior is intentionally conservative:

- Read operations are enabled.
- Write operations are disabled.
- Delete operations are disabled.
- Private-network access is blocked.
- TLS verification is enabled.
- Secrets must use environment-variable references.

## Complete configuration

```yaml
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
  exclude_paths:
    - /admin/*
  include_tags:
    - Public
  exclude_tags:
    - Internal
  methods:
    - GET
  include_deprecated: false

security:
  allow_write_operations: false
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
```

## Source configuration

```yaml
source:
  location: ./openapi.yaml
  format: openapi
  timeout_seconds: 30
```

Supported format values:

- `openapi`
- `swagger`
- `manual`

When `format` is omitted, MCPForge detects the format from the document.

For remote specifications:

```yaml
source:
  location: https://api.example.com/openapi.json
  format: openapi
  base_url: https://api.example.com
```

`base_url` is the runtime API origin. It should be explicitly configured when
the specification URL and API URL differ.

## Authentication

### Bearer token

```yaml
auth:
  type: bearer
  token:
    env: MCPFORGE_API_TOKEN
    required: true
```

### Header API key

```yaml
auth:
  type: api_key
  name: X-API-Key
  location: header
  value:
    env: MCPFORGE_API_KEY
    required: true
```

### Query API key

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

### Static headers

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

Never write secrets directly:

```yaml
# Invalid and rejected
auth:
  type: bearer
  token: "hardcoded-token"
```

## Endpoint filters

```yaml
filters:
  include_paths:
    - /users
    - /users/*
  exclude_paths:
    - /admin/*
    - /internal/*
  include_tags:
    - Public
  exclude_tags:
    - Internal
  methods:
    - GET
  include_deprecated: false
```

Filtering rules:

1. Excluded paths and tags always win.
2. If include paths exist, an endpoint must match one.
3. If include tags exist, an endpoint must contain one.
4. If methods exist, the endpoint method must be included.
5. Deprecated endpoints are excluded unless explicitly enabled.

## Operation safety

```yaml
security:
  allow_write_operations: true
  allow_delete_operations: false
```

Write operations include:

- `POST`
- `PUT`
- `PATCH`

Delete operations include:

- `DELETE`

Enabling writes does not enable deletes.

## Network and payload controls

```yaml
security:
  allowed_hosts:
    - api.example.com
  block_private_networks: true
  max_response_bytes: 5000000
```

`allowed_hosts` uses exact hostname matching. Private-network blocking covers
loopback, private, link-local, reserved, multicast, and unspecified addresses.

## HTTP settings

```yaml
http:
  timeout_seconds: 30
  verify_tls: true
  retry:
    max_attempts: 3
    backoff_seconds: 0.5
```

Retries are bounded. Transient failures such as rate limits and upstream server
errors may be retried according to this policy.
