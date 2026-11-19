# Changelog

All notable changes to MCPForge are documented here.

The project follows a human-readable changelog format. Release versions and
dates may change before the first stable release.

## [Unreleased]

### Added

- Initial MCPForge package architecture.
- Pydantic v2 normalized domain models.
- YAML and JSON project configuration.
- Environment-backed authentication references.
- OpenAPI, Swagger, and manual ingestion pipeline.
- Endpoint filtering and operation safety policies.
- Deterministic MCP tool generation.
- Bearer, API-key, Basic, and static-header authentication providers.
- SSRF and private-network protections.
- Async HTTP execution engine with retries and response limits.
- MCP adapter architecture for stdio and streamable HTTP.
- Typer and Rich CLI foundation.
- Example configurations and technical documentation.

### Security

- Read operations enabled by default.
- Write and delete operations disabled by default.
- Secret values excluded from tool metadata.
- Recursive redaction for diagnostic output.
- Allowed-host enforcement support.
- DNS-based private-network validation.

## [0.1.0] - Initial Development Release

This release establishes the initial repository structure and implementation
contracts for the MCPForge project.

[Unreleased]: https://github.com/AshishVail/mcpforge/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AshishVail/mcpforge/releases/tag/v0.1.0
