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