import json

import httpx
import pytest
from pytest_httpx import HTTPXMock

from patisson_request.core import Response, SelfAsyncService, Service
from patisson_request.errors import ErrorCode, ErrorSchema
from patisson_request.service_responses import (ErrorBodyResponse_4xx,
                                                ErrorBodyResponse_5xx,
                                                TokensSetResponse)
from patisson_request.service_routes import AuthenticationRoute

TEST_LOGIN = 'test_login'
TEST_PASSWORD = 'test_password'
TEST_ACCESS_TOKEN = 'test access token'
TEST_REFRESH_TOKEN = 'test refresh token'


@pytest.fixture(scope="module")
def SelfService() -> SelfAsyncService:
    return SelfAsyncService(
        self_service=Service._TEST,
        login=TEST_LOGIN,
        password=TEST_PASSWORD,
        external_services=[Service.AUTHENTICATION]
    )


@pytest.fixture
def mock_auth(httpx_mock: HTTPXMock) -> HTTPXMock:
    def request_callback(request: httpx.Request) -> httpx.Response:

        if (request.url == "http://localhost/authentication/api/v1/service/jwt/create"
                and request.method == "POST"):
            body = json.loads(request.content.decode('utf-8'))
            assert body['login'] == TEST_LOGIN
            assert body['password'] == TEST_PASSWORD
            return httpx.Response(
                status_code=200,
                content=json.dumps(TokensSetResponse(
                    access_token=TEST_ACCESS_TOKEN,
                    refresh_token=TEST_REFRESH_TOKEN
                ).model_dump())
            )

        elif (request.url == "http://localhost/authentication/api/v1/service/jwt/update"
                and request.method == "POST"):
            body = json.loads(request.content.decode('utf-8'))
            assert request.headers.get('Authorization') == f'Bearer {TEST_ACCESS_TOKEN}'
            assert body['refresh_token'] == TEST_REFRESH_TOKEN
            return httpx.Response(
                status_code=200,
                content=json.dumps(TokensSetResponse(
                    access_token=TEST_ACCESS_TOKEN,
                    refresh_token=TEST_REFRESH_TOKEN
                ).model_dump())
            )

        elif request.url == "http://localhost/authentication/400":
            assert request.headers.get('Authorization') == f'Bearer {TEST_ACCESS_TOKEN}'
            return httpx.Response(
                status_code=400,
                content=json.dumps(
                    {'detail': [ErrorSchema(
                        error=ErrorCode.ACCESS_ERROR
                        ).model_dump()]
                     })
            )

        elif request.url == "http://localhost/authentication/500":
            assert request.headers.get('Authorization') == f'Bearer {TEST_ACCESS_TOKEN}'
            return httpx.Response(
                status_code=500,
                content='test error'
            )

        else:
            raise ValueError('the authentication services mock cannot respond to this request.')

    httpx_mock.add_callback(request_callback, is_reusable=True)
    return httpx_mock


@pytest.mark.asyncio
async def test_200_request_method(SelfService: SelfAsyncService, mock_auth: HTTPXMock):
    response = await SelfService.post_request(
        *-AuthenticationRoute.api.v1.service.jwt.update(
            refresh_token=TEST_REFRESH_TOKEN
        )
    )
    assert isinstance(response, Response)
    assert isinstance(response.body, TokensSetResponse)


@pytest.mark.asyncio
async def test_400_request_method(SelfService: SelfAsyncService, mock_auth: HTTPXMock):
    response = await SelfService.get_request(
        service=Service.AUTHENTICATION, path='400', response_type=TokensSetResponse  # false call
    )
    assert isinstance(response, Response)
    assert isinstance(response.body, ErrorBodyResponse_4xx)


@pytest.mark.asyncio
async def test_500_request_method(SelfService: SelfAsyncService, mock_auth: HTTPXMock):
    response = await SelfService.get_request(
        service=Service.AUTHENTICATION, path='500', response_type=TokensSetResponse  # false call
    )
    assert isinstance(response, Response)
    assert isinstance(response.body, ErrorBodyResponse_5xx)
