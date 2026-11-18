from mcpforge.config.merger import merge_mappings


def test_merge_mappings_recursively_merges_dicts() -> None:
    base = {
        "source": {"location": "./api.yaml", "timeout": 30},
        "tags": ["base"],
    }
    override = {
        "source": {"timeout": 60},
        "tags": ["override"],
    }

    result = merge_mappings(base, override)

    assert result == {
        "source": {"location": "./api.yaml", "timeout": 60},
        "tags": ["override"],
    }
    assert base["source"]["timeout"] == 30


def test_merge_mappings_adds_new_values() -> None:
    result = merge_mappings({"security": {}}, {"security": {"allowed_hosts": ["api.example.com"]}})

    assert result["security"]["allowed_hosts"] == ["api.example.com"]
