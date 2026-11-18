"""Parser for the developer-friendly manual MCPForge YAML format."""

from collections.abc import Mapping
from typing import Any

from mcpforge.domain.models import ApiDocument
from mcpforge.ingestion.errors import SpecificationError
from mcpforge.ingestion.normalization.operation import endpoint_from_operation
from mcpforge.ingestion.normalization.references import ReferenceResolver
from mcpforge.ingestion.source import LoadedDocument


class ManualParser:
    """Parse manual MCPForge endpoint configuration."""

    def parse(self, loaded: LoadedDocument) -> ApiDocument:
        """Parse a manual specification."""

        document = loaded.document
        endpoints_raw = document.get("endpoints")
        if not isinstance(endpoints_raw, list):
            raise SpecificationError("manual specification requires an endpoints list")

        resolver = ReferenceResolver(document)
        endpoints = []

        for index, raw in enumerate(endpoints_raw):
            if not isinstance(raw, Mapping):
                raise SpecificationError(f"manual endpoint {index} must be a mapping")

            path = raw.get("path")
            method = raw.get("method")
            if not isinstance(path, str) or not isinstance(method, str):
                raise SpecificationError(
                    f"manual endpoint {index} requires string path and method"
                )

            endpoint_raw = dict(raw)
            if "request_body" in endpoint_raw and "requestBody" not in endpoint_raw:
                endpoint_raw["requestBody"] = endpoint_raw.pop("request_body")

            parameters = endpoint_raw.get("parameters", [])
            if not isinstance(parameters, list):
                raise SpecificationError(f"manual endpoint {index} parameters must be a list")

            converted_parameters = []
            for parameter in parameters:
                if not isinstance(parameter, Mapping):
                    raise SpecificationError(
                        f"manual endpoint {index} contains an invalid parameter"
                    )
                item = dict(parameter)
                if "location" in item and "in" not in item:
                    item["in"] = item.pop("location")
                converted_parameters.append(item)
            endpoint_raw["parameters"] = converted_parameters

            responses = endpoint_raw.get("responses", {})
            if isinstance(responses, list):
                endpoint_raw["responses"] = {
                    str(item.get("status_code")): item
                    for item in responses
                    if isinstance(item, Mapping)
                }

            endpoints.append(
                endpoint_from_operation(
                    path=path,
                    method=method,
                    raw=endpoint_raw,
                    resolver=resolver,
                )
            )

        return ApiDocument(
            title=str(document.get("name", document.get("title", "Manual API"))),
            version=str(document.get("version", "0.0.0")),
            base_url=document.get("base_url"),
            description=document.get("description"),
            endpoints=endpoints,
            source_format="manual",
            source_name=loaded.source.location,
        )
