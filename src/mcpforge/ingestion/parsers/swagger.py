"""Swagger 2.0 parser."""

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlunsplit

from mcpforge.domain.models import ApiDocument
from mcpforge.ingestion.errors import SpecificationError
from mcpforge.ingestion.normalization.operation import endpoint_from_operation
from mcpforge.ingestion.normalization.references import ReferenceResolver
from mcpforge.ingestion.source import LoadedDocument


class SwaggerParser:
    """Parse Swagger 2.0 documents."""

    def parse(self, loaded: LoadedDocument) -> ApiDocument:
        """Parse one loaded Swagger 2.0 document."""

        document = loaded.document
        if document.get("swagger") != "2.0":
            raise SpecificationError("document is not a Swagger 2.0 specification")

        paths = document.get("paths", {})
        if not isinstance(paths, Mapping):
            raise SpecificationError("Swagger paths must be a mapping")

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
                        swagger=True,
                    )
                )

        info = document.get("info", {})
        info = info if isinstance(info, Mapping) else {}

        return ApiDocument(
            title=str(info.get("title", "Untitled API")),
            version=str(info.get("version", "2.0.0")),
            base_url=self._base_url(document),
            description=info.get("description"),
            endpoints=endpoints,
            source_format="swagger",
            source_name=loaded.source.location,
            extensions={
                "security_definitions": document.get("securityDefinitions", {}),
            },
        )

    @staticmethod
    def _base_url(document: Mapping[str, Any]) -> str | None:
        host = document.get("host")
        if not isinstance(host, str) or not host:
            return None

        schemes = document.get("schemes")
        scheme = "https"
        if isinstance(schemes, list) and schemes and isinstance(schemes[0], str):
            scheme = schemes[0]

        base_path = document.get("basePath", "")
        if not isinstance(base_path, str):
            base_path = ""

        return urlunsplit((scheme, host, base_path.rstrip("/"), "", ""))
