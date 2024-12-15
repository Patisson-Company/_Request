"""
This module defines various classes and structures for handling token payloads in the authentication system. 

It provides base classes and specific implementations for both access and refresh tokens, as well as utilities for serializing and validating token-related data. The module supports client and service roles, along with specific permissions for each.

Key Concepts:
- **TokenBearer**: An enum that represents the type of token bearer, either CLIENT or SERVICE.
- **TokenType**: An enum that represents the type of token, such as ACCESS or REFRESH.
- **BaseTokenPayload**: A generic base class for token payloads containing common fields such as `type`, `iss`, `sub`, `exp`, and `iat`.
- **BaseAccessTokenPayload**: A subclass of `BaseTokenPayload` that extends it with additional fields like `bearer` and `role`, which represent the bearer type (client or service) and the associated role with permissions.
- **ClientAccessTokenPayload**: A subclass of `BaseAccessTokenPayload` specifically for client access tokens. It uses client-specific roles and permissions.
- **ServiceAccessTokenPayload**: A subclass of `BaseAccessTokenPayload` for service access tokens, associated with service-specific roles and permissions.
- **RefreshTokenPayload**: A subclass of `BaseTokenPayload` that represents refresh token payloads.
- **mask_token**: A utility function to mask part of the token string, leaving only the last few characters visible.

Classes and Enums:
- `TokenBearer`: Enum that specifies the bearer type (CLIENT or SERVICE).
- `TokenType`: Enum that specifies the type of token (ACCESS or REFRESH).
- `BaseTokenPayload`: Base class for token payloads that includes common attributes like `type`, `iss`, `sub`, `exp`, and `iat`.
- `BaseAccessTokenPayload`: Extends `BaseTokenPayload`, adding fields for `bearer` and `role` (which represent the token bearer and the associated role).
- `ClientAccessTokenPayload`: A subclass of `BaseAccessTokenPayload` used for client access tokens. It handles client-specific role serialization and validation.
- `ServiceAccessTokenPayload`: A subclass of `BaseAccessTokenPayload` used for service access tokens. It handles service-specific role serialization and validation.
- `RefreshTokenPayload`: A subclass of `BaseTokenPayload` for refresh token payloads, with the same structure but specifically for refresh tokens.
- `mask_token`: A function that masks the characters of the token except for the last `visible_chars` number of characters, providing a way to securely display tokens.

Usage:
    - To create access token payloads for clients or services, instantiate `ClientAccessTokenPayload` or `ServiceAccessTokenPayload`, respectively.
    - Use `RefreshTokenPayload` for managing refresh tokens.
    - `mask_token` can be used to display tokens securely, masking all characters except for the last few.

Example:
    - Creating a client access token payload:
      ```python
      client_payload = ClientAccessTokenPayload(
          type=TokenType.ACCESS,
          iss="MyIssuer",
          sub="UserId123",
          exp=1680000000,
          iat=1670000000,
          bearer=TokenBearer.CLIENT,
          role=ClientRole.MEMBER
      )
      ```
    - Masking a token:
      ```python
      masked_token = mask_token("abcdefghijklmnopqrstuvwxyz", visible_chars=6)
      print(masked_token)  # Output: "**********************yz"
      ```

Dependencies:
    - `pydantic`: Used for defining and validating token payload models.
    - `enum`: Provides the `Enum` base class for defining the `TokenBearer` and `TokenType` enums.
    - `typing`: Used for defining generic types and type aliases.
"""

from enum import Enum
from typing import Generic, TypeAlias, TypeVar, Union, Literal
from pydantic import BaseModel, field_serializer, field_validator

from patisson_request.roles import Role, Permissions, ClientPermissions, ServicePermissions, ServiceRole, ClientRole
from patisson_request.services import Service

Bearer = TypeVar('Bearer', bound='TokenBearer')
Type = TypeVar('Type', bound='TokenType')

UserId: TypeAlias = str
Sub = TypeVar('Sub', bound=Union[UserId, Service])
ServiceSub = TypeVar('ServiceSub', bound=Service)

class TokenBearer(str, Enum):  
    CLIENT = "CLIENT"
    SERVICE = "SERVICE"

class TokenType(str, Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class BaseTokenPayload(BaseModel, Generic[Type, Sub]):
    """
    Base class for token payloads, defining common attributes for any token.

    Attributes:
        type (Type): The type of token (e.g., access, refresh).
        iss (str): The issuer of the token.
        sub (Sub): The subject of the token.
        exp (int): The expiration timestamp of the token.
        iat (int): The issued-at timestamp of the token.
    """
    type: Type
    iss: str
    sub: Sub
    exp: int
    iat: int
    
    class Config:
        arbitrary_types_allowed=True
        use_enum_values = True
    
class BaseAccessTokenPayload(
    BaseTokenPayload[Literal[TokenType.ACCESS], Sub], 
    Generic[Bearer, Permissions, Sub]):
    """
    Base class for access token payloads, extending BaseTokenPayload.

    Attributes:
        bearer (Bearer): The bearer type (e.g., client or service).
        role (Role[Permissions]): The role associated with the token.
    """
    bearer: Bearer
    role: Role[Permissions]
    
    @field_serializer("role")
    def serialize_role(self, role: Role[Permissions]) -> str:
        return str(role)
    
    
class ClientAccessTokenPayload(
    BaseAccessTokenPayload[Literal[TokenBearer.CLIENT], ClientPermissions, UserId]):
    """
    Payload class for client access tokens.
    """

    @field_validator('role', mode='before')
    def parse_role(cls, value) -> Role:
        return ClientRole(str(value))

class ServiceAccessTokenPayload(
    BaseAccessTokenPayload[Literal[TokenBearer.SERVICE], ServicePermissions, ServiceSub], 
    Generic[ServiceSub]):
    """
    Payload class for service access tokens.
    """
    
    @field_validator('role', mode='before')
    def parse_role(cls, value) -> Role:
        return ServiceRole(str(value))

class RefreshTokenPayload(
    BaseTokenPayload[Literal[TokenType.REFRESH], Sub],
    Generic[Sub]):
    """
    Payload class for refresh tokens, extending BaseTokenPayload.
    """
    
    
def mask_token(token: str, visible_chars: int = 4) -> str:
    """
    Closes the token "*" except for the last characters.

    Args:
        token (str)
        visible_chars (int, optional): The displayed number of characters. Defaults to 4.

    Returns:
        str: _description_
    """
    if len(token) <= visible_chars:
        return token
    masked_part = '*' * (len(token) - visible_chars)
    visible_part = token[-visible_chars:]
    return f"{masked_part}{visible_part}"

AccessTokenPayloadType = TypeVar("AccessTokenPayloadType", bound=Union[
    ClientAccessTokenPayload, ServiceAccessTokenPayload])