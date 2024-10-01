from enum import Enum

from pydantic import BaseModel


class TokenBearer(Enum):  
    CLIENT = "CLIENT"
    SERVICE = "SERVICE"

    
class TokenType(Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class ClientPayload(BaseModel):
    iss: str
    sub: str
    exp: int
    iat: int
    role: str
    

class ServicePayload(BaseModel):
    iss: str
    sub: str
    exp: int
    iat: int
    role: str
    

class RefreshPayload(BaseModel):
    iss: str
    sub: str
    exp: int
    iat: int