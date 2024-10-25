import asyncio
import json
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Generic, NoReturn, Optional, Sequence

import httpx
from pydantic import BaseModel

from patisson_request.cache import BaseAsyncTTLCache, RedisAsyncCache
from patisson_request.errors import ErrorCode
from patisson_request.service_responses import (ErrorBodyResponse_4xx,
                                                ErrorBodyResponse_5xx,
                                                ResponseType)
from patisson_request.service_routes import HttpxPostData, RouteAuthentication
from patisson_request.services import Service
from patisson_request.types import *


class Response( BaseModel, Generic[ResponseType]):
    status_code: int
    headers: dict[str, str]
    is_error: bool
    body: ResponseType


@dataclass
class SelfAsyncService:
    self_service: Service
    login: str
    password: str
    external_services: Sequence[Service]
    headers: HeadersType = field(default_factory=lambda: {})
    cache_type: type[BaseAsyncTTLCache] = RedisAsyncCache
    cache_kwargs: Mapping[str, Any] = field(default_factory=lambda: {})
    access_token: Token = ''
    refresh_token: Token = ''
    update_tokens_time: Seconds = 60 * 60 * 4
    default_max_reconnections: int = 3
    default_timeout: float = 3.0
    default_protocol: str = 'http://'
    default_host: str = 'localhost'
    default_use_auth_token: bool = True
    default_header_auth_format: str = 'Bearer {}'
    default_use_cache: bool = True
    
    def __post_init__(self) -> None:
        if self.self_service in self.external_services:
            raise RuntimeError(f'The current service {self.self_service} is in the list of external services')
        self.cache = self.cache_type(service=self.self_service, **self.cache_kwargs)
    
    def activate_tokens_update_task(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.tokens_update_task())
    
    @staticmethod
    def dict_to_bytes(dict_ : dict) -> bytes:
        return json.dumps(dict_).encode('utf-8')
    
    @staticmethod
    def bytes_to_dict(bytes_: bytes) -> dict:
        return json.loads(bytes_)
    
    async def get_tokens_by_login(self) -> None:
        response = await self.post_request(
            *-RouteAuthentication.api.v1.service.jwt.create(
                login=self.login, password=self.password
            ), use_auth_token=False
        )
        if response.is_error:
            raise ConnectionError(f'failed to get jwt tokens. Response: {response}')
        self.access_token = response.body.access_token
        self.refresh_token = response.body.refresh_token
        
    
    async def get_tokens(self) -> None:
        response = await self.post_request(
            *-RouteAuthentication.api.v1.service.jwt.update(
                refresh_token=self.refresh_token
            )
        )
        if response.is_error:
            return await self.get_tokens_by_login()
        self.access_token = response.body.access_token
        self.refresh_token = response.body.refresh_token
    
    
    async def tokens_update_task(self) -> NoReturn:
        while True:
            await self.get_tokens()
            await asyncio.sleep(self.update_tokens_time)
            
    
    def get_url(self, service: Service, path: Path, host: Optional[str] = None,
                 protocol: Optional[str] = None) -> URL:
        return (
            (self.default_protocol if protocol is None else protocol)
            + (self.default_host if host is None else host)
            + '/' + service.value + '/' + path)
        
    
    async def _request(
        self, service: Service, url: URL, method: str, response_type: type[ResponseType],
        add_headers: HeadersType = {}, headers: Optional[HeadersType] = None,
        max_reconnections: Optional[int] = None, timeout: Optional[float] = None, 
        use_auth_token: Optional[bool] = None, header_auth_format: Optional[str] = None,
        **httpx_kwargs) -> Response[ResponseType]:
        
        timeout = self.default_timeout if timeout is None else timeout
        max_reconnections = (self.default_max_reconnections if max_reconnections is None
                             else max_reconnections)
        use_auth_token = (self.default_use_auth_token if use_auth_token is None
                          else use_auth_token)
        header_auth_format = (self.default_header_auth_format if header_auth_format is None
                              else header_auth_format)
        
        if not headers:
            headers = {**self.headers, **add_headers}
            if use_auth_token:
                if self.access_token == '':
                    await self.get_tokens_by_login()
                headers['Authorization'] = header_auth_format.format(self.access_token) 
        
        async with httpx.AsyncClient() as client:
            for i in range(max_reconnections):
                try:
                    httpx_response = await client.request(
                        method, url, headers=headers, timeout=timeout, 
                        **httpx_kwargs)
                    break
                except httpx.ConnectError: pass
            if i + 1 == max_reconnections:
                raise ConnectionError(
                    f'Service {service} did not respond {max_reconnections} times (timeout {timeout})'
                    )
              
        if (httpx_response.status_code == ErrorCode.JWT_EXPIRED
            or httpx_response.status_code == ErrorCode.JWT_INVALID):
            await self.get_tokens()
            return await self._request(
                service=service, url=url, method=method, 
                response_type=response_type, add_headers=add_headers, 
                headers=headers, max_reconnections=max_reconnections,
                timeout=timeout, use_auth_token=use_auth_token, 
                header_auth_format=header_auth_format, **httpx_kwargs)
            
        if httpx_response.status_code >= 500:
            response = Response(
                status_code=httpx_response.status_code,
                headers=httpx_response.headers,  # type: ignore[reportArgumentType]
                is_error=True,
                body=ErrorBodyResponse_5xx(
                    error=httpx_response.text
                )
            )
        elif httpx_response.status_code >= 400:
            response = Response(
                status_code=httpx_response.status_code,
                headers=httpx_response.headers,  # type: ignore[reportArgumentType]
                is_error=True,
                body=ErrorBodyResponse_4xx(
                    **json.loads(httpx_response.text)
                )
            )
        else:
            response = Response(
                status_code=httpx_response.status_code,
                headers=httpx_response.headers,  # type: ignore[reportArgumentType]
                is_error=False,
                body=response_type(
                    **json.loads(httpx_response.text)
                )
            )
            
        return response  # type: ignore[reportReturnType]

    
    async def get_request(
        self, service: Service, path: Path, response_type: type[ResponseType],
        add_headers: HeadersType = {}, headers: Optional[HeadersType] = None, 
        use_cache: Optional[bool] = None, cache_lifetime: Optional[Seconds | timedelta] = None,
        max_reconnections: Optional[int] = None, timeout: Optional[float] = None, 
        protocol: Optional[str] = None, host: Optional[str] = None, 
        use_auth_token: Optional[bool] = None, header_auth_format: Optional[str] = None, 
        **httpx_kwargs) -> Response[ResponseType]:
        
        use_cache = self.default_use_cache if use_cache is None else use_cache
        url = self.get_url(service, path, host, protocol)
        
        if use_cache:
            cache_value = await self.cache.get(url)
            if cache_value: 
                return Response(**self.bytes_to_dict(cache_value))
        
        response = await self._request(
            service=service, url=url, method='GET',
            response_type=response_type, add_headers=add_headers,
            headers=headers, max_reconnections=max_reconnections,
            timeout=timeout, use_auth_token=use_auth_token,
            header_auth_format=header_auth_format, **httpx_kwargs
        )
        
        if use_cache:
            await self.cache.set(
                key=url, time=cache_lifetime,
                value=self.dict_to_bytes(response.model_dump())
                )
            
        return response
    
    
    async def post_request(
        self, service: Service, path: Path, response_type: type[ResponseType],
        post_data: Optional[HttpxPostData] = None, add_headers: HeadersType = {}, 
        headers: Optional[HeadersType] = None, max_reconnections: Optional[int] = None, 
        timeout: Optional[float] = None, protocol: Optional[str] = None, 
        host: Optional[str] = None, use_auth_token: Optional[bool] = None, 
        header_auth_format: Optional[str] = None, **httpx_kwargs) -> Response[ResponseType]:
        
        url = self.get_url(service, path, host, protocol)
        httpx_kwargs |= post_data.model_dump() if post_data is not None else {}
        
        response = await self._request(
            service=service, url=url, method='POST',
            response_type=response_type, add_headers=add_headers,
            headers=headers, max_reconnections=max_reconnections,
            timeout=timeout, use_auth_token=use_auth_token,
            header_auth_format=header_auth_format, **httpx_kwargs
        )
        
        return response