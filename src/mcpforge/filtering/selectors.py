"""Path, method, and tag endpoint selectors."""

from fnmatch import fnmatch

from mcpforge.config.models import EndpointFilterConfig
from mcpforge.domain.models import Endpoint


def _matches_path(path: str, patterns: list[str]) -> bool:
    return any(fnmatch(path, pattern) or pattern in path for pattern in patterns)


def matches_selectors(endpoint: Endpoint, config: EndpointFilterConfig) -> bool:
    """Apply deterministic selector precedence.

    Exclusions always win. If an include selector category is configured,
    the endpoint must match that category.
    """

    if _matches_path(endpoint.path, config.exclude_paths):
        return False
    if set(endpoint.tags) & set(config.exclude_tags):
        return False

    if config.include_paths and not _matches_path(endpoint.path, config.include_paths):
        return False
    if config.include_tags and not set(endpoint.tags) & set(config.include_tags):
        return False
    if config.methods and endpoint.method not in config.methods:
        return False
    if endpoint.deprecated and not config.include_deprecated:
        return False
    return True
