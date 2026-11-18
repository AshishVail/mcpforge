from pathlib import Path

from mcpforge.ingestion.loaders.file import load_file
from mcpforge.ingestion.parsers.manual import ManualParser
from mcpforge.ingestion.source import Source


def test_manual_parser_normalizes_fixture() -> None:
    path = Path(__file__).parents[2] / "fixtures" / "manual" / "basic.yaml"

    document = ManualParser().parse(load_file(Source(str(path))))

    assert document.source_format == "manual"
    assert document.base_url == "https://inventory.example.com"
    assert len(document.endpoints) == 2

    list_items = document.endpoints[0]
    assert list_items.operation_id == "list_items"
    assert list_items.parameters[0].name == "limit"
