# Supported Specifications

MCPForge supports OpenAPI, Swagger, and a manual endpoint format.

## OpenAPI 3.0

Supported features include:

- `openapi: 3.0.x`
- `info`
- `servers`
- `paths`
- HTTP operations
- `operationId`
- `summary`
- `description`
- `tags`
- Path, query, header, and cookie parameters
- `requestBody`
- JSON media types
- Response status codes
- Response schemas
- Local `$ref` references
- `components.schemas`

Example:

```yaml
openapi: 3.0.3
info:
  title: Example API
  version: "1.0.0"
paths:
  /users/{id}:
    get:
      operationId: get_user
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: User
```

## OpenAPI 3.1

OpenAPI 3.1 documents use the same normalized endpoint pipeline. JSON Schema
features are preserved where they can be represented by the internal schema
model.

Supported features include:

- `openapi: 3.1.x`
- Servers
- Paths and operations
- Parameters
- Request bodies
- Responses
- Components
- Local references

## Swagger 2.0

Supported Swagger features include:

- `swagger: "2.0"`
- `host`
- `basePath`
- `schemes`
- `info`
- `paths`
- `operationId`
- Parameters using `in: path`
- Parameters using `in: query`
- Parameters using `in: header`
- Parameters using `in: body`
- `definitions`
- Response schemas
- `securityDefinitions`

The Swagger base URL is constructed from:

```text
scheme://host/basePath
```

For example:

```yaml
host: api.example.com
basePath: /v1
schemes:
  - https
```

becomes:

```text
https://api.example.com/v1
```

## Manual format

Manual specifications are useful when an API has no formal OpenAPI document.

```yaml
name: Inventory API
version: "1.0.0"
base_url: https://inventory.example.com

endpoints:
  - operation_id: list_items
    method: GET
    path: /items
    summary: List inventory items
    parameters:
      - name: limit
        location: query
        required: false
        schema:
          type: integer
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
```

Manual parameters use `location`:

- `path`
- `query`
- `header`
- `cookie`

Manual request bodies use `request_body`:

```yaml
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
```

## Local references

Local JSON Pointer references are supported:

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
```

```yaml
schema:
  $ref: "#/components/schemas/User"
```

External references are intentionally restricted and should be resolved before
passing a document to MCPForge.

## Unsupported or limited features

Depending on the specification, the following may require manual adaptation:

- External `$ref` URLs
- Multipart file upload semantics
- Complex callback objects
- Webhooks
- WebSocket operations
- Vendor-specific serialization rules
- Arbitrary custom authentication flows
- Deeply dynamic schemas that cannot be represented as strict JSON Schema

When a specification cannot express an operation safely, define that operation
manually or exclude it through configuration.
