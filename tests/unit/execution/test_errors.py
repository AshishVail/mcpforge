from mcpforge.execution.errors import error_for_status


def test_common_status_categories() -> None:
    assert error_for_status(400).category == "bad_request"
    assert error_for_status(401).category == "authentication_failed"
    assert error_for_status(403).category == "authorization_failed"
    assert error_for_status(404).category == "not_found"
    assert error_for_status(429).retryable
    assert error_for_status(500).retryable
