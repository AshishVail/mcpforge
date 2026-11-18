"""Specification source loaders."""

from mcpforge.ingestion.loaders.file import load_file
from mcpforge.ingestion.loaders.remote import load_remote
from mcpforge.ingestion.source import LoadedDocument, Source

__all__ = ["LoadedDocument", "Source", "load_file", "load_remote"]
