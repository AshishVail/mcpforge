"""OpenAPI 3.0 and 3.1 parser."""

from collections.abc import Mapping
from typing import Any

from mcpforge.domain.models import ApiDocument
from mcpforge.ingestion.errors import SpecificationError
from mcpforge.ingestion.normalization.operation import endpoint_from_operation
from mcpforge.ingestion.normalization.references import ReferenceResolver
from mcpforge.ingestion.source import LoadedDocument


class OpenAPIParser:
    """Parse OpenAPI 3.0 and 3.1 documents."""

    def parse(self, loaded: LoadedDocument) -> ApiDocument:
        """Parse one loaded OpenAPI document."""

        document = loaded.document
        version = document.get("openapi")
        if not isinstance(version, str) or not version.startswith(("3.0", "3.1")):
            raise SpecificationError("document is not an OpenAPI 3.0 or 3.1 specification")

        paths = document.get("paths", {})
        if not isinstance(paths, Mapping):
            raise SpecificationError("OpenAPI paths must be a mapping")

        resolver = ReferenceResolver(document)
        endpoints = []

        for path, path_item in paths.items():
            if not isinstance(path, str) or not isinstance(path_item, Mapping):
                continue

            common_parameters = path_item.get("parameters", [])
            if not isinstance(common_parameters, list):
                common_parameters = []

            for method, operation in path_item.items():
                if method.lower() not in {
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "head",
                    "options",
                }:
                    continue
                if not isinstance(operation, Mapping):
                    raise SpecificationError(f"operation {method} {path} must be a mapping")

                endpoints.append(
                    endpoint_from_operation(
                        path=path,
                        method=method,
                        raw=operation,
                        resolver=resolver,
                        path_parameters=common_parameters,
                    )
                )

        info = document.get("info", {})
        if not isinstance(info, Mapping):
            info = {}

        return ApiDocument(
            title=str(info.get("title", "Untitled API")),
            version=str(info.get("version", version)),
            base_url=self._base_url(document),
            description=(
                str(info["description"]) if isinstance(info.get("description"), str) else None
            ),
            endpoints=endpoints,
            source_format="openapi",
            source_name=loaded.source.location,
        )

    @staticmethod
    def _base_url(document: Mapping[str, Any]) -> str | None:
        servers = document.get("servers")
        if isinstance(servers, list) and servers:
            first = servers[0]
            if isinstance(first, Mapping) and isinstance(first.get("url"), str):
                return str(first["url"])

        return None
