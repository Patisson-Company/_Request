from typing import Mapping, Sequence, TypeAlias

from httpx._types import RequestContent, RequestData, RequestFiles

Encodable: TypeAlias = bytes | memoryview | str | int | float
Seconds: TypeAlias = int

HeadersType = Mapping[str, str]
URL: TypeAlias = str
Path: TypeAlias = str
Token: TypeAlias = str | bytes

GraphqlField: TypeAlias = str
NestedGraphqlFields: TypeAlias = Mapping[str, Sequence]