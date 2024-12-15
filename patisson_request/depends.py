"""
This module contains utility functions and decorators for verifying and handling service and client tokens, along with OpenTelemetry tracing integration.

It includes functions to verify service and client tokens using the `SelfAsyncService` class, which communicates with an authentication service to validate the tokens. Additionally, the module provides decorators that automatically add OpenTelemetry spans with relevant token attributes for tracking and tracing.

Key Functions and Classes:
- **verify_service_token_dep**: A function that verifies a service access token by making a request to the authentication service. If the token is invalid, it raises an `InvalidJWT` exception.
- **dep_opentelemetry_service_decorator**: A decorator for the `verify_service_token_dep` function that starts an OpenTelemetry span and attaches various token attributes, such as issuer, subject, expiration, and role, to the span for tracing.
- **verify_client_token_dep**: A function that verifies a client access token by making a request to the authentication service. If the token is invalid, it raises an `InvalidJWT` exception.
- **dep_opentelemetry_client_decorator**: A decorator for the `verify_client_token_dep` function that starts an OpenTelemetry span and attaches various token attributes, such as issuer, subject, expiration, and role, to the span for tracing.

Key Concepts:
- **Service Token Verification**: The `verify_service_token_dep` function is responsible for validating service tokens. It sends the token to an authentication service for verification and returns the corresponding `ServiceAccessTokenPayload` if valid.
- **Client Token Verification**: The `verify_client_token_dep` function performs the same operation but for client tokens, returning a `ClientAccessTokenPayload` if the token is valid.
- **OpenTelemetry Integration**: The decorators `dep_opentelemetry_service_decorator` and `dep_opentelemetry_client_decorator` are designed to integrate token validation with OpenTelemetry tracing. These decorators create spans to monitor and trace the verification process, including capturing important attributes like the token’s validity and associated role.

Usage:
    - To use the token verification functions, pass an instance of `SelfAsyncService` and a token as arguments to `verify_service_token_dep` or `verify_client_token_dep`. These functions will return the respective token payload if verification is successful.
    - To use the decorators, apply `dep_opentelemetry_service_decorator` or `dep_opentelemetry_client_decorator` to any token verification function. These decorators will automatically trace the function’s execution and add useful metadata to the OpenTelemetry spans.

Example Usage:
    - Verifying a service token with OpenTelemetry tracing:
      ```python
      @dep_opentelemetry_service_decorator(tracer)
      async def some_service_function(self_service: SelfAsyncService, access_token: Token):
          return await verify_service_token_dep(self_service, access_token)
      ```
    - Verifying a client token with OpenTelemetry tracing:
      ```python
      @dep_opentelemetry_client_decorator(tracer)
      async def some_client_function(self_service: SelfAsyncService, access_token: Token):
          return await verify_client_token_dep(self_service, access_token)
      ```

Dependencies:
    - `opentelemetry`: For integrating tracing and creating spans.
    - `patisson_request.core`: For the `SelfAsyncService` class used to verify tokens.
    - `patisson_request.errors`: For handling JWT-related errors via `InvalidJWT`.
    - `patisson_request.jwt_tokens`: For the `ServiceAccessTokenPayload` and `ClientAccessTokenPayload` classes.
    - `patisson_request.types`: For the `Token` type used in token verification.

Exceptions:
    - `InvalidJWT`: Raised when a token is invalid or fails verification.

Attributes added to OpenTelemetry spans:
    - `service.is_access_token_valid`: Whether the service access token is valid.
    - `service.access_token_iss`: Issuer of the service token.
    - `service.access_token_sub`: Subject of the service token.
    - `service.access_token_exp`: Expiration time of the service token.
    - `service.access_token_iat`: Issued-at time of the service token.
    - `service.role`: Role associated with the service access token.
    
    - `client.is_access_token_valid`: Whether the client access token is valid.
    - `client.access_token_iss`: Issuer of the client token.
    - `client.access_token_sub`: Subject of the client token.
    - `client.access_token_exp`: Expiration time of the client token.
    - `client.access_token_iat`: Issued-at time of the client token.
    - `client.role`: Role associated with the client access token.
"""

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
        InvalidJWT: Client JWT is uncorrected

    Returns:
        ClientAccessTokenPayload
    """
    token = await self_service.client_verify(client_access_token=str(access_token))
    if token is False:
        raise InvalidJWT(ErrorSchema(
            error=ErrorCode.CLIENT_JWT_INVALID,
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