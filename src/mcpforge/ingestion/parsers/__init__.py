"""Specification parsers."""

from mcpforge.ingestion.parsers.base import Parser
from mcpforge.ingestion.parsers.manual import ManualParser
from mcpforge.ingestion.parsers.openapi import OpenAPIParser
from mcpforge.ingestion.parsers.swagger import SwaggerParser

__all__ = ["ManualParser", "OpenAPIParser", "Parser", "SwaggerParser"]
