from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from patisson_request.types import Token, Seconds


class AuthenticationRequest:
    
    class CreateClient(BaseModel):
        client_id: str
        client_role: str
        expire_in: Optional[Seconds] = None
        
    class CreateService(BaseModel):
        login: str
        password: str
        
    class Verify(BaseModel):
        access_token: Token

    class UpdateClient(BaseModel):
        client_access_token: Token
        client_refresh_token: Token
        expire_in: Optional[Seconds] = None
        
    class UpdateService(BaseModel):
        refresh_token: Token


class UsersRequest:
    
    class CreateUser(BaseModel):
        username: str
        password: str
        first_name: Optional[str] = None
        last_name: Optional[str] = None
        avatar: Optional[str] = None
        about: Optional[str] = None
        expire_in: Optional[Seconds] = None

    class CreateLibrary(BaseModel):
        book_id: str
        user_id: str 
        status: int
        
    class CreateBan(BaseModel):
        user_id: str
        reason: int
        comment: str 
        end_date: datetime