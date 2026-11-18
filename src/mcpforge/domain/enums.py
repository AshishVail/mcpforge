"""Domain enumerations."""

from enum import StrEnum


class HttpMethod(StrEnum):
    """Supported HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ParameterLocation(StrEnum):
    """Locations in which endpoint parameters can be transmitted."""

    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"


class OperationSafety(StrEnum):
    """High-level operation safety classification."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"


class AuthType(StrEnum):
    """Supported authentication mechanisms."""

    NONE = "none"
    BEARER = "bearer"
    API_KEY = "api_key"
    BASIC = "basic"
    STATIC_HEADERS = "static_headers"
