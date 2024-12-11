from functools import wraps
from typing import Awaitable, Callable

from opentelemetry.trace import Tracer

from patisson_request.core import SelfAsyncService
from patisson_request.errors import ErrorCode, ErrorSchema, InvalidJWT
from patisson_request.jwt_tokens import (ClientAccessTokenPayload,
                                         ServiceAccessTokenPayload)
from patisson_request.types import Token


async def verify_service_token_dep(self_service: SelfAsyncService, 
                                   access_token: Token
                                   ) -> ServiceAccessTokenPayload:
    """
    Makes a request to the authentication service to verify the service token

    Args:
        self_service (SelfAsyncService): instance of the class SelfAsyncService
        access_token (Token): the token that requires verification

    Raises:
        InvalidJWT: JWT is uncorrected

    Returns:
        ServiceAccessTokenPayload
    """
    token = await self_service.service_verify(service_access_token=str(access_token))
    if token is False:
        raise InvalidJWT(ErrorSchema(
            error=ErrorCode.JWT_INVALID,
        ))
    return token

def dep_opentelemetry_service_decorator(tracer: Tracer):
    """
    A decorator for dep that adds span with token attributes

    Args:
        tracer (Tracer)
    """
    def decorator(func: Callable[..., Awaitable[ServiceAccessTokenPayload]]):
        @wraps(func)
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


async def verify_client_token_dep(self_service: SelfAsyncService, 
                                  access_token: Token
                                  ) -> ClientAccessTokenPayload:
    """
    Makes a request to the authentication service to verify the client token

    Args:
        self_service (SelfAsyncService): instance of the class SelfAsyncService
        access_token (Token): the token that requires verification

    Raises:
        InvalidJWT: JWT is uncorrected

    Returns:
        ClientAccessTokenPayload
    """
    token = await self_service.client_verify(client_access_token=str(access_token))
    if token is False:
        raise InvalidJWT(ErrorSchema(
            error=ErrorCode.JWT_INVALID,
        ))
    return token

def dep_opentelemetry_client_decorator(tracer: Tracer):
    """
    A decorator for dep that adds span with token attributes

    Args:
        tracer (Tracer)
    """
    def decorator(func: Callable[..., Awaitable[ClientAccessTokenPayload]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span("verify-client-token") as span:
                token = await func(*args, **kwargs)
                span.set_attribute("client.is_access_token_valid", True)
                span.set_attribute("client.access_token_iss", token.iss)
                span.set_attribute("client.access_token_sub", token.sub)
                span.set_attribute("client.access_token_exp", token.exp)
                span.set_attribute("client.access_token_iat", token.iat)
                span.set_attribute("client.role", token.role.name)
            return token
        return wrapper
    return decorator