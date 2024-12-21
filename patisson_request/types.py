from typing import Mapping, Sequence, TypeAlias

from httpx._types import RequestContent, RequestData, RequestFiles  # noqa: F401

Encodable: TypeAlias = bytes | memoryview | str | int | float
Seconds: TypeAlias = int

HeadersType = Mapping[str, str]
URL: TypeAlias = str
Path: TypeAlias = str
Token: TypeAlias = str

GraphqlField: TypeAlias = str
NestedGraphqlFields: TypeAlias = Mapping[str, Sequence]
