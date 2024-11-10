from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ErrorCode(Enum):
    INVALID_PARAMETERS = 'the passed parameters are not correct'
    BAD_CREDENTIALS = 'invalid credentials'
    VALIDATE_ERROR = 'validation error'
    
    ACCESS_ERROR = 'there is no permission for this call'
    JWT_INVALID = 'invalid jwt'
    JWT_EXPIRED = 'jwt has expired'
    JWT_SUB_NOT_EQUAL = 'jwt sub in access and refresh tokens are not equal'

    CLIENT_ACCESS_ERROR = 'client there is no permission for this call'
    CLIENT_JWT_INVALID = 'client has an invalid jwt'
    CLIENT_JWT_EXPIRED = 'client has an jwt has expired'
    CLIENT_JWT_SUB_NOT_EQUAL = 'client jwt sub in access and refresh tokens are not equal'

class ErrorSchema(BaseModel):
    error: ErrorCode
    extra: Optional[str] = None
    
    class Config:  
        use_enum_values = True
        

class ValidateError(Exception): ...

class UniquenessError(Exception): ...

class InvalidJWT(Exception): 
    
    def __init__(self, error: ErrorSchema) -> None:
        super().__init__()
        self.error_schema = error
        
class UnauthorizedServiceError(Exception): ...