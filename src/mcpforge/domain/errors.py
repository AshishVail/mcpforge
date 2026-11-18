"""Domain-level exceptions."""


class MCPForgeError(Exception):
    """Base exception for expected MCPForge failures."""


class DomainValidationError(MCPForgeError):
    """Raised when a normalized domain object violates an invariant."""


class ConfigurationError(MCPForgeError):
    """Raised when project configuration cannot be loaded or validated."""
