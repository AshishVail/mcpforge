# Security Model

MCPForge is designed to expose APIs to AI clients without treating AI-generated
input as trusted.

## Security principles

1. Fail closed.
2. Keep credentials outside configuration values.
3. Require explicit permission for mutations.
4. Validate network targets before connecting.
5. Redact secrets before logging or returning diagnostics.
6. Bound retries, timeouts, and payload sizes.
7. Keep security checks in a reusable central layer.

## Operation safety

Read operations are enabled by default:

- `GET`
- `HEAD`
- `OPTIONS`

Write operations require explicit configuration:

- `POST`
- `PUT`
- `PATCH`

Delete operations require a separate explicit configuration flag:

- `DELETE`

```yaml
security:
  allow_write_operations: false
  allow_delete_operations: false
```

This protects against accidental destructive actions caused by ambiguous model
intent, prompt injection, or incorrectly generated arguments.

## SSRF protection

By default, MCPForge blocks requests to:

- `localhost`
- Loopback IPv4 and IPv6 addresses
- RFC1918 private IPv4 ranges
- Link-local addresses
- Reserved addresses
- Multicast addresses
- Unspecified addresses
- Other special-purpose address ranges recognized by Python's IP library

DNS results are resolved and checked before a request is sent. Redirect handling
must apply the same validation to the destination host.

## Allowed hosts

For production deployments, configure an explicit host allowlist:

```yaml
security:
  allowed_hosts:
    - api.example.com
    - uploads.example.com
```

Host matching is exact. Wildcard hostnames are not interpreted implicitly.

## Credentials

Credentials must be referenced through environment variables:

```yaml
auth:
  type: bearer
  token:
    env: MCPFORGE_API_TOKEN
    required: true
```

Credentials must not be stored in:

- `mcpforge.yaml`
- OpenAPI specifications
- Generated tool descriptions
- Tool input schemas
- Source code
- Git history
- Error messages
- Debug logs

## Secret redaction

MCPForge recursively redacts sensitive fields such as:

- `Authorization`
- `Cookie`
- `Set-Cookie`
- `token`
- `password`
- `secret`
- `api_key`
- `access_token`
- `client_secret`

Known secret values can also be scrubbed from diagnostic strings.

## Payload limits

Large responses can overflow an AI client's context window and increase resource
consumption. Configure a maximum response size:

```yaml
security:
  max_response_bytes: 5000000
```

Oversized responses are converted into structured errors and the raw body is not
returned to the AI client.

## Timeouts and retries

Requests must have bounded timeouts:

```yaml
http:
  timeout_seconds: 30
  retry:
    max_attempts: 3
    backoff_seconds: 0.5
```

Retries are limited to transient failures. Authentication, authorization,
validation, and not-found failures are not blindly retried.

## TLS

TLS verification is enabled by default:

```yaml
http:
  verify_tls: true
```

Disabling verification should be limited to controlled development environments.
It is not recommended for production.

## Deployment recommendations

For remote deployments:

- Use HTTPS.
- Place the server behind an authenticated gateway.
- Restrict inbound network access.
- Use a secret manager.
- Rotate credentials regularly.
- Enable audit logging.
- Apply external rate limiting.
- Run with a dedicated least-privilege service account.
- Keep the MCP SDK and HTTP dependencies updated.
- Review endpoint allowlists before enabling writes or deletes.

MCPForge is a security layer, not a replacement for upstream API authorization.
The upstream API must still enforce identity, permissions, tenant isolation, and
business rules.
