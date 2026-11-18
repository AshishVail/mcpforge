from mcpforge.domain.enums import HttpMethod
from mcpforge.domain.models import Endpoint
from mcpforge.filtering.policies import SafetyPolicy


def endpoint(method: HttpMethod, deprecated: bool = False) -> Endpoint:
    return Endpoint(path="/items", method=method, deprecated=deprecated)


def test_read_operations_are_allowed_by_default() -> None:
    assert SafetyPolicy().allows(endpoint(HttpMethod.GET))


def test_writes_require_explicit_permission() -> None:
    assert not SafetyPolicy().allows(endpoint(HttpMethod.POST))
    assert SafetyPolicy(allow_write_operations=True).allows(endpoint(HttpMethod.POST))


def test_deletes_require_separate_permission() -> None:
    assert not SafetyPolicy(allow_write_operations=True).allows(endpoint(HttpMethod.DELETE))
    assert SafetyPolicy(allow_delete_operations=True).allows(endpoint(HttpMethod.DELETE))


def test_deprecated_operations_are_excluded() -> None:
    assert not SafetyPolicy().allows(endpoint(HttpMethod.GET, deprecated=True))
    assert SafetyPolicy(include_deprecated=True).allows(endpoint(HttpMethod.GET, deprecated=True))
