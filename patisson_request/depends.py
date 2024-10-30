from typing import Awaitable, Callable
from opentelemetry.trace import Tracer

from patisson_request.core import SelfAsyncService
from patisson_request.errors import ErrorCode, ErrorSchema, InvalidJWT
from patisson_request.jwt_tokens import ServiceAccessTokenPayload
from patisson_request.types import Token


async def verify_service_token_dep(self_service: SelfAsyncService, access_token: Token
                                    ) -> ServiceAccessTokenPayload:
    token = await self_service.service_verify(service_access_token=str(access_token))
    if token is False:
        ...
        raise InvalidJWT(ErrorSchema(
            error=ErrorCode.JWT_INVALID,
        ))
    return token


def dep_jaeger_decorator(tracer: Tracer):
    def decorator(func: Callable[..., Awaitable[ServiceAccessTokenPayload]]):
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span("verify-service-token") as span:
                token = await func(*args, **kwargs)
                span.set_attribute("service.is_access_token_valid", True)
                span.set_attribute("service.access_token_iss", token.iss)
                span.set_attribute("service.access_token_sub", token.sub)
                span.set_attribute("service.access_token_exp", token.exp)
                span.set_attribute("service.access_token_iat", token.iat)
                span.set_attribute("service.role", token.role.name)
            return token
        return wrapper
    return decorator
