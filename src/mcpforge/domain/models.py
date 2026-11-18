"""Normalized parser-independent REST API models."""

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mcpforge.domain.enums import HttpMethod, OperationSafety, ParameterLocation


class JsonSchema(BaseModel):
    """Conservative JSON Schema representation used by the internal model."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: str | None = None
    title: str | None = None
    description: str | None = None
    format: str | None = None
    enum: list[object] | None = None
    default: object | None = None
    required: list[str] = Field(default_factory=list)
    properties: dict[str, "JsonSchema"] = Field(default_factory=dict)
    items: "JsonSchema | None" = None
    additional_properties: bool | "JsonSchema" | None = Field(
        default=None,
        alias="additionalProperties",
    )

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        if self.type == "object" and self.items is not None:
            raise ValueError("object schemas cannot define items")
        if self.type == "array" and self.properties:
            raise ValueError("array schemas cannot define properties")
        unknown = set(self.required) - set(self.properties)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"required fields are not defined: {names}")
        return self


class Parameter(BaseModel):
    """A path, query, header, or cookie parameter."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=1, pattern=r"^[A-Za-z0-9._-]+$")]
    location: ParameterLocation
    required: bool = False
    description: str | None = None
    schema: JsonSchema = Field(default_factory=JsonSchema)
    deprecated: bool = False
    example: object | None = None

    @model_validator(mode="after")
    def validate_path_requirement(self) -> Self:
        if self.location is ParameterLocation.PATH and not self.required:
            raise ValueError("path parameters must be required")
        return self


class RequestBody(BaseModel):
    """Normalized request body definition."""

    model_config = ConfigDict(extra="forbid")

    required: bool = False
    content_type: str = "application/json"
    schema: JsonSchema = Field(default_factory=JsonSchema)
    description: str | None = None


class ResponseDefinition(BaseModel):
    """One possible normalized endpoint response."""

    model_config = ConfigDict(extra="forbid")

    status_code: Annotated[int, Field(ge=100, le=599)]
    description: str | None = None
    content_type: str | None = None
    schema: JsonSchema | None = None


class Endpoint(BaseModel):
    """A complete normalized REST endpoint."""

    model_config = ConfigDict(extra="forbid")

    operation_id: str | None = None
    path: Annotated[str, Field(min_length=1, pattern=r"^/")]
    method: HttpMethod
    summary: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    parameters: list[Parameter] = Field(default_factory=list)
    request_body: RequestBody | None = None
    responses: list[ResponseDefinition] = Field(default_factory=list)
    deprecated: bool = False
    safety: OperationSafety | None = None

    @model_validator(mode="after")
    def validate_endpoint(self) -> Self:
        path_names = {
            segment[1:-1]
            for segment in self.path.split("/")
            if segment.startswith("{") and segment.endswith("}")
        }
        defined_names = {
            parameter.name
            for parameter in self.parameters
            if parameter.location is ParameterLocation.PATH
        }
        missing = path_names - defined_names
        if missing:
            raise ValueError(f"path parameters are not defined: {', '.join(sorted(missing))}")

        seen: set[str] = set()
        duplicates: set[str] = set()
        for parameter in self.parameters:
            if parameter.name in seen:
                duplicates.add(parameter.name)
            seen.add(parameter.name)
        if duplicates:
            raise ValueError(f"duplicate parameter names: {', '.join(sorted(duplicates))}")
        return self


class ApiDocument(BaseModel):
    """The stable parser output consumed by future pipeline stages."""

    model_config = ConfigDict(extra="forbid")

    title: str = "Untitled API"
    version: str = "0.0.0"
    base_url: str | None = None
    description: str | None = None
    endpoints: list[Endpoint] = Field(default_factory=list)
    source_format: str | None = None
    source_name: str | None = None
    extensions: dict[str, object] = Field(default_factory=dict)
