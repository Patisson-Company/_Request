# pyright: reportPossiblyUnboundVariable=false
"""
This module provides classes and methods for interacting with external services via HTTP requests, 
handling authentication, retry logic, and caching responses.

Classes:
    - SelfService: A service client that constructs URLs, sends HTTP requests (GET/POST), handles 
      retries, manages authentication tokens, and supports caching of responses.
    - Response: A generic class representing an HTTP response with a dynamic body type, useful for 
      handling various service responses.

The `SelfService` class contains methods for sending requests to services, verifying authentication tokens,
and managing response data, including caching and handling errors. The `Response` class models HTTP responses 
with fields for status code, headers, error flags, and the response body. Both classes are used for service 
interactions and error management in a robust and scalable manner.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Generic, Literal, Mapping, NoReturn, Optional, Sequence

import httpx
from pydantic import BaseModel

from patisson_request import jwt_tokens
from patisson_request.cache import BaseAsyncTTLCache, RedisAsyncCache
from patisson_request.errors import ErrorCode, UnauthorizedServiceError, DuplicatHeadersError
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
    """
    Represents an HTTP response with a generic body type.

    Attributes:
        status_code (int): The HTTP status code of the response.
        headers (dict[str, str]): The headers of the response.
        is_error (bool): A flag indicating whether the response represents an error.
        body (ResponseBodyTypeVar): The body of the response, which can be of any type specified by `ResponseBodyTypeVar`.
    """
    status_code: int
    headers: dict[str, str]
    is_error: bool
    body: ResponseBodyTypeVar 

NULL = ''


@dataclass
class SelfAsyncService:
    """
    Represents a service that interacts with external services asynchronously.

    Attributes:
        self_service (Service): The internal service that is being represented.
        login (str): The login credentials for the service.
        password (str): The password credentials for the service.
        external_services (Sequence[Service]): A sequence of external services that the service interacts with.
        headers (HeadersType): Custom headers to be used for the service's requests.
        cache_type (type[BaseAsyncTTLCache]): The cache type to use for the service, default is RedisAsyncCache.
        cache_kwargs (Mapping[str, Any]): Additional arguments for the cache type.
        access_token (Token): The access token for authentication, default is an empty string (`NULL`).
        refresh_token (Token): The refresh token for authentication, default is an empty string (`NULL`).
        update_tokens_time (Seconds): The time interval (in seconds) for token refresh, default is 4 hours.
        default_max_reconnections (int): The default maximum number of reconnections, default is 3.
        default_timeout (float): The default timeout for requests, default is 3 seconds.
        default_protocol (str): The default protocol for requests, default is `http://`.
        default_host (str): The default host for requests, default is `localhost`.
        default_use_auth_token (bool): A flag indicating whether to use an authentication token, default is `True`.
        default_header_auth_format (str): The format for the authentication header, default is `Bearer {}`.
        default_use_cache (bool): A flag indicating whether to use cache, default is `True`.
        default_use_graphql_cache (bool): A flag indicating whether to use GraphQL cache, default is `True`.
        default_users_auth_service (Service): The default authentication service, default is `Service.USERS`.
        use_telemetry (bool): A flag indicating whether to use telemetry, default is `True`.
        logger_object (Optional[logging.Logger]): The logger instance to use for logging, default is `None`.
        logging_level (int): The logging level for the logger, default is `logging.DEBUG`.
    """
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
            from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
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
        """
        Converts a dictionary to a bytes representation, using UTF-8 encoding.

        Args:
            dict_ (dict): The dictionary to convert.

        Returns:
            bytes: The UTF-8 encoded byte representation of the dictionary.
        """
        return json.dumps(dict_, default=EmptyField.empty_field_encoder).encode('utf-8')
    
    @staticmethod
    def bytes_to_dict(bytes_: bytes) -> dict:
        """
        Converts a bytes object to a dictionary.

        Args:
            bytes_ (bytes): The bytes to convert.

        Returns:
            dict: The dictionary representation of the bytes.
        """
        return json.loads(bytes_)
    
    @staticmethod
    def remove_empty_fields_from_response_body(body: ResponseBodyAlias | BaseModel) -> dict:
        """
        Recursively removes fields with empty values from a response body, 
        including nested models and lists of models.

        Args:
            body (ResponseBodyAlias | BaseModel): The response body to clean up.

        Returns:
            dict: The cleaned response body without empty fields.
        """
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
        """
        Starts the token update task asynchronously in the event loop.

        This method initiates a background task that periodically updates the tokens.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.tokens_update_task())
        self.logger.debug('the token update task has been started')
    
    def extract_token_from_header(self, header: str, header_format: Optional[str] = None) -> str:
        """
        Extracts the token from an authorization header.

        Args:
            header (str): The authorization header.
            header_format (Optional[str], optional): The format of the authorization header 
                (default is 'Bearer {}').

        Returns:
            str: The extracted token.
        """
        if not header_format: header_format = self.default_header_auth_format
        header_format_ = header_format.replace('{}', '').strip()
        return header.replace(header_format_, '')
        
    async def get_tokens_by_login(self) -> None:
        """
        Fetches JWT tokens using the provided login and password.

        Makes a request to the authentication service to obtain access and refresh tokens.
        Raises a `ConnectionError` if the request fails.

        Raises:
            ConnectionError: If the request to obtain tokens fails.
        """
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
        """
        Fetches JWT tokens using the refresh token.

        Makes a request to the authentication service to update the tokens using the refresh token.
        If the refresh token is not valid or the request fails, it attempts to get tokens by login.

        Raises:
            ConnectionError: If both token fetching methods fail.
        """
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
        """
        Returns the access token, fetching it if it's not already available.

        If the access token is `NULL`, it attempts to fetch tokens by calling `get_tokens()`.

        Returns:
            str: The access token.
        """
        if self.access_token != NULL: return self.access_token
        else: 
            await self.get_tokens()
            return self.access_token
    
    
    async def tokens_update_task(self) -> NoReturn:
        """
        Continuously updates tokens at a specified interval.

        This task runs indefinitely, fetching new tokens using the refresh token 
        and sleeping for the duration specified in `update_tokens_time`.

        This method does not return, it runs as an infinite loop.
        """
        while True:
            await self.get_tokens()
            await asyncio.sleep(self.update_tokens_time)
            
            
    async def service_verify(self, service_access_token: str, 
                             service: Optional[Service] = None) -> (
                                Literal[False] 
                                | ServiceAccessTokenPayload):
        """
        Verifies the validity of the service's access token.

        This method checks the validity of the service access token by first looking for it in the cache.
        If the token is valid in the cache, it returns the payload. If not, it sends a request to verify the token.
        
        Args:
            service_access_token (str): The access token of the service to verify.
            service (Optional[Service], optional): The specific service to verify the token for. 
                If not provided, the service value is derived from the token payload.

        Returns:
            Literal[False]: If the token is invalid or expired.
            ServiceAccessTokenPayload: The payload from the token if it is valid.
        """
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
        """
        Verifies the validity of the client's access token.

        This method checks the validity of the client access token by first looking for it in the cache.
        If the token is valid in the cache, it returns the payload. If not, it sends a request to verify the token.

        Args:
            client_access_token (str): The access token of the client to verify.
            users_auth_service (Optional[Service], optional): The authentication service to verify the token for.
                Defaults to the default user authentication service if not provided.

        Returns:
            Literal[False]: If the token is invalid or expired.
            ClientAccessTokenPayload: The payload from the token if it is valid.
        """
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
        """
        Constructs the full URL for a given service and path.

        Args:
            service (Service): The service for which the URL is being constructed.
            path (Path): The path to append to the URL.
            host (Optional[str], optional): The host to use in the URL. Defaults to `localhost` if not provided.
            protocol (Optional[str], optional): The protocol to use. Defaults to `http://` if not provided.

        Returns:
            URL: The full URL as a string.
        """
        return (
            (self.default_protocol if protocol is None else protocol)
            + (self.default_host if host is None else host)
            + '/' + service.value + '/' + path)
        
    
    async def _request(
        self, service: Service, url: URL, method: str, response_type: type[ResponseBodyTypeVar],
        add_headers: Optional[HeadersType] = None, headers: Optional[HeadersType] = None,
        max_reconnections: Optional[int] = None, timeout: Optional[float] = None, 
        use_auth_token: Optional[bool] = None, header_auth_format: Optional[str] = None,
        _return_nonetype_response_body: bool = False,  # the response body will be of type dict
        **httpx_kwargs) -> Response[ResponseBodyTypeVar]:
        """
        Sends an HTTP request with the given parameters and returns the deserialized response.

        Args:
            service (Service): The service to which the request is made.
            url (URL): The URL to which the request is sent.
            method (str): The HTTP method for the request (e.g., 'GET' or 'POST').
            response_type (type[ResponseBodyTypeVar]): The type into which the response will be deserialized.
            add_headers (Optional[HeadersType]): Additional headers to include in the request.
            headers (Optional[HeadersType]): Headers to include in the request.
            max_reconnections (Optional[int]): Maximum number of reconnection attempts.
            timeout (Optional[float]): Timeout for the request.
            use_auth_token (Optional[bool]): Whether to include the authentication token in the headers.
            header_auth_format (Optional[str]): The format for the authorization header.
            _return_nonetype_response_body (bool): If True, the response body will be a dictionary.
            **httpx_kwargs: Additional parameters for the HTTP request.

        Returns:
            Response[ResponseBodyTypeVar]: The service's response, including status and response body.
        """
        
        if service == self.self_service:
            e = 'Services cannot make requests to themselves'
            self.logger.critical(e)
            raise RuntimeError(e)
        
        timeout = self.default_timeout if timeout is None else int(timeout)
        if timeout < 0:
            raise ValueError('the timeout cannot be less than 0')
        max_reconnections = (self.default_max_reconnections if max_reconnections is None
                             else int(max_reconnections))
        if max_reconnections < 2:
            raise ValueError('the max_reconnections cannot be less than 2')
        use_auth_token = (self.default_use_auth_token if use_auth_token is None
                          else bool(use_auth_token))
        header_auth_format = (self.default_header_auth_format if header_auth_format is None
                              else header_auth_format)
        
        if not headers:
            if add_headers:
                headers = {**self.headers, **add_headers}
            else:
                headers = {**self.headers}
                
            if use_auth_token:
                if self.access_token == NULL:
                    await self.get_tokens_by_login()
                headers['Authorization'] = header_auth_format.format(self.access_token) 
                
        if len(headers.values()) != len(set(headers.values())):
            raise DuplicatHeadersError("Duplicate headers")
        
        async with httpx.AsyncClient() as client:
            for i in range(max_reconnections):
                try:
                    httpx_response = await client.request(
                        method, url, headers=headers, timeout=timeout, 
                        **httpx_kwargs)
                    if service == Service.AUTHENTICATION: break
                    if not httpx_response.status_code >= 400:
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
                header_auth_format=header_auth_format, 
                _return_nonetype_response_body=_return_nonetype_response_body,
                **httpx_kwargs)
            
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
                body={}  # type: ignore[reportArgumentType]
            )
            if _return_nonetype_response_body:
                response.body = dict(**json.loads(httpx_response.text))
            else:
                response.body = response_type(**json.loads(httpx_response.text))
            
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
        """
        Sends a GET request to the specified service and returns the deserialized response.

        Args:
            service (Service): The service to which the request is made.
            path (Path): The path of the API endpoint.
            response_type (type[ResponseBodyTypeVar]): The type into which the response will be deserialized.
            add_headers (HeadersType): Additional headers to include in the request.
            headers (Optional[HeadersType]): Headers to include in the request.
            use_cache (Optional[bool]): Whether to use caching for the response.
            cache_lifetime (Optional[Seconds | timedelta]): The lifetime of the cached response.
            max_reconnections (Optional[int]): Maximum number of reconnection attempts.
            timeout (Optional[float]): Timeout for the request.
            protocol (Optional[str]): The protocol to use for the URL (e.g., 'http', 'https').
            host (Optional[str]): The host to use for the URL.
            use_auth_token (Optional[bool]): Whether to include the authentication token in the headers.
            header_auth_format (Optional[str]): The format for the authorization header.
            **httpx_kwargs: Additional parameters for the HTTP request.

        Returns:
            Response[ResponseBodyTypeVar]: The service's response, including status and response body.
        """
        use_cache = self.default_use_cache if use_cache is None else bool(use_cache)
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
        use_graphql_cache: Optional[bool] = None, graphql_cache_lifetime: Optional[Seconds | timedelta] = None,
        **httpx_kwargs) -> Response[ResponseBodyTypeVar]:
        """
        Sends a POST request to the specified service with optional POST data and returns the deserialized response.

        Args:
            service (Service): The service to which the request is made.
            path (Path): The path of the API endpoint.
            response_type (type[ResponseBodyTypeVar]): The type into which the response will be deserialized.
            post_data (Optional[HttpxPostData]): Optional data to include in the POST request.
            is_graphql (bool): Whether the request is a GraphQL request.
            add_headers (HeadersType): Additional headers to include in the request.
            headers (Optional[HeadersType]): Headers to include in the request.
            max_reconnections (Optional[int]): Maximum number of reconnection attempts.
            timeout (Optional[float]): Timeout for the request.
            protocol (Optional[str]): The protocol to use for the URL (e.g., 'http', 'https').
            host (Optional[str]): The host to use for the URL.
            use_auth_token (Optional[bool]): Whether to include the authentication token in the headers.
            header_auth_format (Optional[str]): The format for the authorization header.
            use_graphql_cache (Optional[bool]): Whether to use caching for the GraphQL response.
            graphql_cache_lifetime (Optional[Seconds | timedelta]): The lifetime of the cached GraphQL response.
            **httpx_kwargs: Additional parameters for the HTTP request.

        Returns:
            Response[ResponseBodyTypeVar]: The service's response, including status and response body.
        """
        is_graphql = bool(is_graphql)
        use_graphql_cache = bool(use_graphql_cache)
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
            if not isinstance(response.body, dict):
                response_copy = response.model_copy(deep=True)
                response_copy.body = self.remove_empty_fields_from_response_body(response_copy.body)  # type: ignore[reportAttributeAccessIssue]
            else:
                response_copy = response
            await self.cache.set(
                key=cache_key, time=graphql_cache_lifetime, 
                value=self.dict_to_bytes(response_copy.model_dump()) 
            )
        
        return response