"""
This module defines error handling classes and schemas for managing exceptions and error responses in the system.

It includes custom exceptions, error codes, and a Pydantic schema for returning error details in HTTP responses. The error codes cover a range of issues, including invalid parameters, bad credentials, and JWT validation errors. Custom exceptions are defined for handling specific cases, such as invalid JWTs or service authorization errors.

Key Concepts:
- **ErrorCode**: Enum that defines a set of error codes used throughout the application. Each code represents a specific error message, such as invalid parameters, bad credentials, or JWT-related issues (e.g., JWT expiration or invalid sub).
- **ErrorSchema**: A Pydantic model that represents the error response structure. It includes the error code and an optional extra message for additional details.
- **ValidateError**: A custom exception class for validation errors.
- **DuplicateHeadersError**: A custom exception class for handling duplicate header errors.
- **UniquenessError**: A custom exception class for handling uniqueness-related errors (e.g., duplicate data).
- **InvalidJWT**: A custom exception class that is raised when there is an issue with a JWT, such as invalid JWT, expiration, or mismatched sub. The exception contains an `ErrorSchema` that describes the error.
- **UnauthorizedServiceError**: A custom exception class for unauthorized service access.

Classes and Enums:
- `ErrorCode`: Enum that defines specific error codes and their corresponding messages, covering a wide range of authentication, authorization, and validation errors.
- `ErrorSchema`: A Pydantic model that encapsulates error information, including the error code and an optional additional message.
- `ValidateError`: Exception raised for validation errors.
- `DuplicateHeadersError`: Exception raised when duplicate headers are encountered.
- `UniquenessError`: Exception raised when a uniqueness constraint is violated.
- `InvalidJWT`: Exception raised for invalid JWTs, containing an `ErrorSchema` to provide detailed error information.
- `UnauthorizedServiceError`: Exception raised when a service is not authorized to access a particular resource.

Usage:
    - To raise an error, instantiate the appropriate exception class, such as `InvalidJWT` or `UnauthorizedServiceError`, and provide any necessary details (e.g., `ErrorSchema` for JWT errors).
    - Use the `ErrorSchema` model to structure error responses for HTTP exceptions, returning the corresponding error code and optional extra message.

Example:
    - Raising an invalid JWT error:
      ```python
      error_schema = ErrorSchema(error=ErrorCode.JWT_INVALID, extra="JWT token format is incorrect")
      raise InvalidJWT(error_schema)
      ```
    - Returning an error response in an API endpoint:
      ```python
      return ErrorSchema(error=ErrorCode.BAD_CREDENTIALS, extra="Credentials not found").model_dump()
      ```
"""

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
    """
    Pydantic model for http exception
    """
    error: ErrorCode
    extra: Optional[str] = None
    
    class Config:  
        use_enum_values = True

class ValidateError(Exception): ...

class DuplicatHeadersError(Exception): ...

class UniquenessError(Exception): ...

class InvalidJWT(Exception): 
    
    def __init__(self, error: ErrorSchema) -> None:
        super().__init__()
        self.error_schema = error
        
class UnauthorizedServiceError(Exception): ...