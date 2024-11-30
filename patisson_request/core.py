import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Generic, Literal, Mapping, NoReturn, Optional, Sequence

import httpx
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from pydantic import BaseModel

from patisson_request import jwt_tokens
from patisson_request.cache import BaseAsyncTTLCache, RedisAsyncCache
from patisson_request.errors import ErrorCode, UnauthorizedServiceError
from patisson_request.graphql.models.books_model import EmptyField
from patisson_request.jwt_tokens import (ClientAccessTokenPayload,
                                         ServiceAccessTokenPayload,
                                         TokenBearer)
from patisson_request.service_responses import (ErrorBodyResponse_4xx,
                                                ErrorBodyResponse_5xx,
                                                ResponseBodyAlias,
                                                ResponseBodyTypeVar)
from patisson_request.service_routes import (USERS_VERIFY_ROUTE,
                                             AuthenticationRoute,
                                             HttpxPostData)
from patisson_request.services import Service
from patisson_request.types import URL, HeadersType, Path, Seconds, Token


class Response(BaseModel, Generic[ResponseBodyTypeVar]):
    status_code: int
    headers: dict[str, str]
    is_error: bool
    body: ResponseBodyTypeVar
    
    

NULL = ''

@dataclass
class SelfAsyncService:
    self_service: Service
    login: str
    password: str
    external_services: Sequence[Service]
    headers: HeadersType = field(default_factory=lambda: {})
    cache_type: type[BaseAsyncTTLCache] = RedisAsyncCache
    cache_kwargs: Mapping[str, Any] = field(default_factory=lambda: {})
    access_token: Token = NULL
    refresh_token: Token = NULL
    update_tokens_time: Seconds = 60 * 60 * 4
    default_max_reconnections: int = 3
    default_timeout: float = 3.0
    default_protocol: str = 'http://'
    default_host: str = 'localhost'
    default_use_auth_token: bool = True
    default_header_auth_format: str = 'Bearer {}'
    default_use_cache: bool = True
    default_use_graphql_cache: bool = True
    default_users_auth_service: Service = Service.USERS
    use_telemetry: bool = True
    logger_object: Optional[logging.Logger] = None
    logging_level: int = logging.DEBUG
    
    def __post_init__(self) -> None:
        if not self.logger_object:
            self.logger = logging.getLogger()
            self.logger.addHandler(logging.NullHandler())
        else:
            self.logger = self.logger_object
        self.logger.setLevel(self.logging_level)
        
        if self.self_service in self.external_services:
            raise RuntimeError(f'The current service {self.self_service} is in the list of external services')
        self.cache = self.cache_type(
            service=self.self_service, 
            logger=self.logger,
            **self.cache_kwargs)
        
        if self.use_telemetry:
            HTTPXClientInstrumentor().instrument()
        
        logging_msg = NULL
        secret_var = [
            'password'
        ]
        for attr, value in vars(self).items():
            if attr in secret_var: continue
            logging_msg += f" - {attr}: {value}\n"
        self.logger.info(f'Initialized {self.__class__}: \n{logging_msg}')
    
    @staticmethod
    def dict_to_bytes(dict_ : dict) -> bytes:
        return json.dumps(dict_, default=EmptyField.empty_field_encoder).encode('utf-8')
    
    @staticmethod
    def bytes_to_dict(bytes_: bytes) -> dict:
        return json.loads(bytes_)
    
    @staticmethod
    def remove_empty_fields_from_response_body(body: ResponseBodyAlias | BaseModel) -> dict:
        cleaned_data = {}
        for field, value in body.model_dump(exclude_unset=True, exclude_defaults=True).items():
            if isinstance(value, BaseModel):
                cleaned_data[field] = SelfAsyncService.remove_empty_fields_from_response_body(value)
            elif isinstance(value, list):
                cleaned_list = []
                for item in value:
                    if isinstance(item, BaseModel):
                        cleaned_item = SelfAsyncService.remove_empty_fields_from_response_body(item)
                        cleaned_list.append(cleaned_item)
                    elif item != EmptyField():
                        cleaned_list.append(item)
                cleaned_data[field] = cleaned_list
            elif value != EmptyField():
                cleaned_data[field] = value
        return cleaned_data
    
    def activate_tokens_update_task(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.tokens_update_task())
        self.logger.debug('the token update task has been started')
    
    def extract_token_from_header(self, header: str, header_format: Optional[str] = None) -> str:
        if not header_format: header_format = self.default_header_auth_format
        header_format_ = header_format.replace('{}', '').strip()
        return header.replace(header_format_, '')
        
    async def get_tokens_by_login(self) -> None:
        response = await self.post_request(
            *-AuthenticationRoute.api.v1.service.jwt.create(
                login=self.login, password=self.password
            ), use_auth_token=False
        )
        if response.is_error:
            self.logger.critical('Failed to get a tokens by login')
            raise ConnectionError(f'failed to get jwt tokens. Response: {response}')
        self.access_token = response.body.access_token
        self.refresh_token = response.body.refresh_token
        self.logger.info('tokens have been received by login')
        
    
    async def get_tokens(self) -> None:
        response = await self.post_request(
            *-AuthenticationRoute.api.v1.service.jwt.update(
                refresh_token=self.refresh_token
            )
        )
        if response.is_error:
            self.logger.warning('Failed to get a tokens')
            return await self.get_tokens_by_login()
        self.access_token = response.body.access_token
        self.refresh_token = response.body.refresh_token
        self.logger.info('tokens have been received')
    
    
    async def get_access_token(self) -> str:
        if self.access_token != NULL: return self.access_token
        else: 
            await self.get_tokens()
            return self.access_token
    
    
    async def tokens_update_task(self) -> NoReturn:
        while True:
            await self.get_tokens()
            await asyncio.sleep(self.update_tokens_time)
            
            
    async def service_verify(self, service_access_token: str, 
                             service: Optional[Service] = None) -> (
                                Literal[False] 
                                | ServiceAccessTokenPayload):
        cache_value = await self.cache.get(service_access_token + TokenBearer.SERVICE.value)
        if cache_value:
            return ServiceAccessTokenPayload(**self.bytes_to_dict(cache_value))
        elif cache_value is bytes(False):
            self.logger.warning(f'service {service} has an invalid token')
            return False
        else:  # cache_value is None
            response = await self.post_request(
                *-AuthenticationRoute.api.v1.service.jwt.verify(service_access_token)
            )
            payload = response.body.payload  # type: ignore[reportAssignmentType]
            if not response.body.is_verify:
                await self.cache.set(service_access_token + TokenBearer.SERVICE.value, bytes(False))
                self.logger.warning(f'service {service} has an invalid token')
                return False
            payload: jwt_tokens.ServiceAccessTokenPayload
            if service is not None and Service(payload.sub).value != service.value:
                await self.cache.set(service_access_token + TokenBearer.SERVICE.value, bytes(False))
                self.logger.critical(f'service {service} has someone elses token')
                return False
            await self.cache.set(service_access_token + TokenBearer.SERVICE.value, 
                                 self.dict_to_bytes(payload.model_dump()), 
                                 payload.exp - int(time.time()))
            self.logger.info(f'the service token {service} is valid')
            return payload
        
    
    async def client_verify(self, client_access_token: str,
        users_auth_service: Optional[Service] = None) -> (
        Literal[False] | ClientAccessTokenPayload):
        if not users_auth_service: users_auth_service = self.default_users_auth_service
        
        cache_value = await self.cache.get(client_access_token + TokenBearer.CLIENT.value)
        if cache_value:
            return ClientAccessTokenPayload(**self.bytes_to_dict(cache_value))
        elif cache_value is bytes(False):
            self.logger.info(f'client has an invalid token')
            return False
        else:  # cache_value is None
            response = await self.post_request(
                *-USERS_VERIFY_ROUTE[users_auth_service](client_access_token)
            )
            payload = response.body.payload  # type: ignore[reportAssignmentType]
            if not response.body.is_verify:
                await self.cache.set(client_access_token + TokenBearer.CLIENT.value, bytes(False))
                self.logger.info(f'client has an invalid token')
                return False
            payload: jwt_tokens.ClientAccessTokenPayload
            await self.cache.set(client_access_token + TokenBearer.CLIENT.value, 
                                 self.dict_to_bytes(payload.model_dump()), 
                                 payload.exp - int(time.time()))
            self.logger.info(f'the client token is valid')
            return payload
    
    def get_url(self, service: Service, path: Path, host: Optional[str] = None,
                 protocol: Optional[str] = None) -> URL:
        return (
            (self.default_protocol if protocol is None else protocol)
            + (self.default_host if host is None else host)
            + '/' + service.value + '/' + path)
        
    
    async def _request(
        self, service: Service, url: URL, method: str, response_type: type[ResponseBodyTypeVar],
        add_headers: HeadersType = {}, headers: Optional[HeadersType] = None,
        max_reconnections: Optional[int] = None, timeout: Optional[float] = None, 
        use_auth_token: Optional[bool] = None, header_auth_format: Optional[str] = None,
        **httpx_kwargs) -> Response[ResponseBodyTypeVar]:
        
        if service == self.self_service:
            e = 'Services cannot make requests to themselves'
            self.logger.critical(e)
            raise RuntimeError(e)
        
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
                if self.access_token == NULL:
                    await self.get_tokens_by_login()
                headers['Authorization'] = header_auth_format.format(self.access_token) 
        
        async with httpx.AsyncClient() as client:
            for i in range(max_reconnections):
                try:
                    httpx_response = await client.request(
                        method, url, headers=headers, timeout=timeout, 
                        **httpx_kwargs)
                    
                    if service == Service.AUTHENTICATION: break
                    response_access_token = self.extract_token_from_header(
                        httpx_response.headers['Authorization']
                        )
                    is_verify = await self.service_verify(response_access_token, service)
                    if not is_verify:
                        raise UnauthorizedServiceError                            
                    break
                
                except httpx.ConnectError: 
                    self.logger.warning(f'service {service} did not respond')
                
                except KeyError:  # httpx_response.headers['Authorization']
                    self.logger.warning(f'service {service} does not have an authorization header')
                
                except UnauthorizedServiceError:
                    self.logger.warning(f'service {service} has an invalid token')
                    
            if i + 1 == max_reconnections:
                msg = f'Service {service} did not respond {max_reconnections} times (timeout {timeout})'
                self.logger.critical(msg)
                raise ConnectionError(msg)  
              
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
        self.logger.info(f'request: {method} {url}, response: {response.status_code}')
        return response  # type: ignore[reportReturnType]

    
    async def get_request(
        self, service: Service, path: Path, response_type: type[ResponseBodyTypeVar],
        add_headers: HeadersType = {}, headers: Optional[HeadersType] = None, 
        use_cache: Optional[bool] = None, cache_lifetime: Optional[Seconds | timedelta] = None,
        max_reconnections: Optional[int] = None, timeout: Optional[float] = None, 
        protocol: Optional[str] = None, host: Optional[str] = None, 
        use_auth_token: Optional[bool] = None, header_auth_format: Optional[str] = None, 
        **httpx_kwargs) -> Response[ResponseBodyTypeVar]:
        
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
        
        if use_cache and not response.is_error:
            await self.cache.set(
                key=url, value=self.dict_to_bytes(response.model_dump()), 
                time=cache_lifetime
                )
            
        return response
    
    
    async def post_request(
        self, service: Service, path: Path, response_type: type[ResponseBodyTypeVar],
        post_data: Optional[HttpxPostData] = None, is_graphql: bool = False,
        add_headers: HeadersType = {}, headers: Optional[HeadersType] = None, 
        max_reconnections: Optional[int] = None, timeout: Optional[float] = None, 
        protocol: Optional[str] = None, host: Optional[str] = None, 
        use_auth_token: Optional[bool] = None, header_auth_format: Optional[str] = None, 
        use_graphql_cache: Optional[bool] = None, cache_lifetime: Optional[Seconds | timedelta] = None,
        **httpx_kwargs) -> Response[ResponseBodyTypeVar]:
        
        use_cache = is_graphql and (use_graphql_cache or self.default_use_graphql_cache)
        url = self.get_url(service, path, host, protocol)
        httpx_kwargs |= post_data.model_dump() if post_data is not None else {}
        
        if use_cache:
            cache_key = str(url+str(post_data.json_))  # type: ignore[reportOptionalMemberAccess]
            cache_value = await self.cache.get(cache_key) 
            if cache_value: 
                value = self.bytes_to_dict(cache_value)        
                value['body'] = response_type(**value['body'])
                return Response(**value)
        
        response = await self._request(
            service=service, url=url, method='POST',
            response_type=response_type, add_headers=add_headers,
            headers=headers, max_reconnections=max_reconnections,
            timeout=timeout, use_auth_token=use_auth_token,
            header_auth_format=header_auth_format, **httpx_kwargs
        )

        if use_cache and not response.is_error:
            response_copy = response.model_copy(deep=True)
            response_copy.body = self.remove_empty_fields_from_response_body(response_copy.body)  # type: ignore[reportAttributeAccessIssue]
            await self.cache.set(
                key=cache_key, time=cache_lifetime, 
                value=self.dict_to_bytes(response_copy.model_dump()) 
            )
        
        return response