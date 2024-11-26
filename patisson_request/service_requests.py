from datetime import datetime
from typing import Any, Generic, Optional

from pydantic import BaseModel, Field

from patisson_request.service_responses import ResponseBodyTypeVar
from patisson_request.services import Service
from patisson_request.types import (Path, RequestContent, RequestData,
                                    RequestFiles, Seconds, Token)


class HttpxPostData(BaseModel):
    json_: Optional[Any] = Field(None, alias='json')
    data: Optional[RequestData] = None
    content: Optional[RequestContent] = None   
    files: Optional[RequestFiles] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def model_dump(self, *args, **kwargs):
        kwargs.setdefault('by_alias', True)
        return super().model_dump(*args, **kwargs)
    
    
class BaseRequest(BaseModel, Generic[ResponseBodyTypeVar]):
    service: Service
    path: Path
    response_type: type[ResponseBodyTypeVar]    
    
    def __neg__(self) -> tuple[Service, Path, type[ResponseBodyTypeVar]]:
        return (self.service, self.path, self.response_type)

class GetRequest(BaseRequest[ResponseBodyTypeVar], Generic[ResponseBodyTypeVar]):
    ''''''

class PostRequest(BaseRequest[ResponseBodyTypeVar], Generic[ResponseBodyTypeVar]):
    post_data: HttpxPostData = HttpxPostData()  # type: ignore[reportCallIssue]
    is_graphql: bool = False
    
    def __neg__(self) -> tuple[Service, Path, type[ResponseBodyTypeVar], HttpxPostData, bool]:
        base_params = super().__neg__()
        return *base_params, self.post_data, self.is_graphql


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
        
    class VerifyUser(BaseModel):
        access_token: str
        
    class UpdateUser(BaseModel):
        refresh_token: str