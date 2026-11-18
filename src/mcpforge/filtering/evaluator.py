"""Endpoint filtering service."""

from mcpforge.config.models import EndpointFilterConfig, SecurityConfig
from mcpforge.domain.models import ApiDocument
from mcpforge.filtering.policies import SafetyPolicy
from mcpforge.filtering.selectors import matches_selectors


def filter_document(
    document: ApiDocument,
    filters: EndpointFilterConfig | None = None,
    security: SecurityConfig | None = None,
) -> ApiDocument:
    """Return a new document containing only permitted endpoints."""

    selector_config = filters or EndpointFilterConfig()
    safety = SafetyPolicy.from_config(
        security or SecurityConfig(),
        include_deprecated=selector_config.include_deprecated,
    )
    endpoints = [
        endpoint
        for endpoint in document.endpoints
        if matches_selectors(endpoint, selector_config) and safety.allows(endpoint)
    ]
    return document.model_copy(update={"endpoints": endpoints})
