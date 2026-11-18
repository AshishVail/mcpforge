"""Generated tool descriptions."""


def endpoint_description(
    summary: str | None,
    description: str | None,
    method: str,
    path: str,
) -> str:
    """Build a concise deterministic description."""

    text = summary or description
    if text:
        return text.strip()
    return f"Execute {method.upper()} {path}."
