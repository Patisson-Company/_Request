from typing import Any, Generic, List, Optional, Union
from patisson_request import jwt_tokens 
from pydantic import BaseModel, Field

from patisson_request.graphql.queries import format_strings
from patisson_request.graphql.queries import build_query
from patisson_request.service_responses import AuthenticationResponse, BooksResponse, HealthCheckBodyResponse, ResponseType
from patisson_request.services import Service
from patisson_request.types import *

__all__ = [
    'RouteAuthentication',
    'RouteBooks'
]

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
    
    
class BaseRequest(BaseModel, Generic[ResponseType]):
    service: Service
    path: Path
    response_type: type[ResponseType]    
    
    def __neg__(self) -> tuple[Service, Path, type[ResponseType]]:
        return (self.service, self.path, self.response_type)

class GetRequest(BaseRequest[ResponseType], Generic[ResponseType]):
    ''''''

class PostRequest(BaseRequest[ResponseType], Generic[ResponseType]):
    post_data: HttpxPostData = HttpxPostData()  # type: ignore[reportCallIssue]
    
    def __neg__(self) -> tuple[Service, Path, type[ResponseType], HttpxPostData]:
        base_params = super().__neg__()
        return (
            *base_params, self.post_data
        )


def url_params(**kwargs) -> str:
    query = ''
    for kwarg in kwargs:
        if kwarg: 
            query += f'{kwarg}={kwargs[kwarg]}&'
    return query


class RouteAuthentication:
    
    @staticmethod
    def health() -> GetRequest[HealthCheckBodyResponse]:
        return GetRequest(
            service=Service.AUTHENTICATION,
            path='health',
            response_type=HealthCheckBodyResponse
        )
        
    class api:
        class v1:
            class client:
                class jwt:
                    
                    @staticmethod
                    def create(client_id: str, client_role: str,
                               expire_in: Optional[Seconds] = None
                               ) -> GetRequest[AuthenticationResponse.TokensSet]:
                        path = 'api/v1/client/jwt/create?{}'
                        return GetRequest(
                            service=Service.AUTHENTICATION,
                            path=path.format(
                                url_params(
                                    client_id=client_id, 
                                    client_role=client_role, 
                                    expire_in=expire_in
                                )
                            ), 
                            response_type=AuthenticationResponse.TokensSet
                        )
                    
                    @staticmethod
                    def verify(client_access_token: Token
                               ) -> GetRequest[jwt_tokens.ClientPayload]:
                        path = 'api/v1/client/jwt/verify?{}'
                        return GetRequest(
                            service=Service.AUTHENTICATION,
                            path=path.format(
                                url_params(
                                    client_access_token=client_access_token
                                )
                            ),
                            response_type=jwt_tokens.ClientPayload
                        )
                    
                    @staticmethod
                    def update(client_access_token: Token,
                               client_refresh_token: Token,
                               expire_in: Optional[Seconds]
                               ) -> GetRequest[AuthenticationResponse.TokensSet]:
                        path = 'api/v1/client/jwt/update?{}'
                        return GetRequest(
                            service=Service.AUTHENTICATION,
                            path=path.format(
                                url_params(
                                    client_access_token=client_access_token,
                                    client_refresh_token=client_refresh_token,
                                    expire_in=expire_in
                                )
                            ),
                            response_type=AuthenticationResponse.TokensSet
                        )
            
            class service: 
                class jwt:
                    
                    @staticmethod
                    def create(login: str, password: str
                               ) -> GetRequest[AuthenticationResponse.TokensSet]:
                        path = 'api/v1/service/jwt/create?{}'
                        return GetRequest(
                            service=Service.AUTHENTICATION,
                            path=path.format(
                                url_params(
                                    login=login, 
                                    password=password
                                )
                            ),
                            response_type=AuthenticationResponse.TokensSet
                        )
                    
                    @staticmethod
                    def verify(verified_service_jwt: Token
                               ) -> GetRequest[jwt_tokens.ServicePayload]:
                        path = 'api/v1/service/jwt/verify?{}'
                        return GetRequest(
                            service=Service.AUTHENTICATION,
                            path=path.format(
                                url_params(
                                    verified_service_jwt=verified_service_jwt
                                )
                            ),
                            response_type=jwt_tokens.ServicePayload
                        )
                    
                    @staticmethod
                    def update(refresh_token: Token
                               ) -> GetRequest[AuthenticationResponse.TokensSet]:
                        path = 'api/v1/service/jwt/update?{}'
                        return GetRequest(
                            service=Service.AUTHENTICATION,
                            path=path.format(
                                url_params(
                                    refresh_token=refresh_token
                                )
                            ),
                            response_type=AuthenticationResponse.TokensSet
                        )


class RouteBooks:
    
    @staticmethod
    def health() -> GetRequest[HealthCheckBodyResponse]:
        return GetRequest(
            service=Service.BOOKS,
            path='health',
            response_type=HealthCheckBodyResponse
        )
    
    class graphql:

        @staticmethod
        def books(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            ids: Optional[List[str]] = None,
            titles: Optional[List[str]] = None,
            like_title: Optional[str] = None,
            google_ids: Optional[List[str]] = None,
            publishers: Optional[List[str]] = None,
            exact_publishedDate: Optional[str] = None,
            from_publishedDate: Optional[str] = None,
            to_publishedDate: Optional[str] = None,
            like_description: Optional[str] = None,
            exact_pageCount: Optional[int] = None,
            from_pageCount: Optional[int] = None,
            to_pageCount: Optional[int] = None,
            maturityRating: Optional[str] = None,
            languages: Optional[List[str]] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            search: Optional[List[str]] = None
        ) -> PostRequest[BooksResponse.Gbooks]:
            args = [
                f'ids: {format_strings(ids)}' if ids is not None else None,
                f'titles: {format_strings(titles)}' if titles is not None else None,
                f'like_title: "{like_title}"' if like_title is not None else None,
                f'google_ids: {format_strings(google_ids)}' if google_ids is not None else None,
                f'publishers: {format_strings(publishers)}' if publishers is not None else None,
                f'exact_publishedDate: "{exact_publishedDate}"' if exact_publishedDate is not None else None,
                f'from_publishedDate: "{from_publishedDate}"' if from_publishedDate is not None else None,
                f'to_publishedDate: "{to_publishedDate}"' if to_publishedDate is not None else None,
                f'like_description: "{like_description}"' if like_description is not None else None,
                f'exact_pageCount: {exact_pageCount}' if exact_pageCount is not None else None,
                f'from_pageCount: {from_pageCount}' if from_pageCount is not None else None,
                f'to_pageCount: {to_pageCount}' if to_pageCount is not None else None,
                f'maturityRating: "{maturityRating}"' if maturityRating is not None else None,
                f'languages: {format_strings(languages)}' if languages is not None else None,
                f'offset: {offset}' if offset is not None else None,
                f'limit: {limit}' if limit is not None else None,
                f'search: {format_strings(search)}' if search is not None else None,
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.Gbooks,
                post_data=HttpxPostData(
                    json={'query': build_query(type='query', name='books', args=args, fields=fields)}
                    )
            )
        
        @staticmethod
        def booksDeep(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            ids: Optional[List[str]] = None,
            titles: Optional[List[str]] = None,
            like_title: Optional[str] = None,
            google_ids: Optional[List[str]] = None,
            publishers: Optional[List[str]] = None,
            exact_publishedDate: Optional[str] = None,
            from_publishedDate: Optional[str] = None,
            to_publishedDate: Optional[str] = None,
            like_description: Optional[str] = None,
            exact_pageCount: Optional[int] = None,
            from_pageCount: Optional[int] = None,
            to_pageCount: Optional[int] = None,
            maturityRating: Optional[str] = None,
            languages: Optional[List[str]] = None,
            authors: Optional[List[str]] = None,
            categories: Optional[List[str]] = None,
            limit: Optional[int] = None,
            search: Optional[List[str]] = None
        ) -> PostRequest[BooksResponse.GbooksDeep]:
            args = [
                f'ids: {format_strings(ids)}' if ids is not None else None,
                f'titles: {format_strings(titles)}' if titles is not None else None,
                f'like_title: "{like_title}"' if like_title is not None else None,
                f'google_ids: {format_strings(google_ids)}' if google_ids is not None else None,
                f'publishers: {format_strings(publishers)}' if publishers is not None else None,
                f'exact_publishedDate: "{exact_publishedDate}"' if exact_publishedDate is not None else None,
                f'from_publishedDate: "{from_publishedDate}"' if from_publishedDate is not None else None,
                f'to_publishedDate: "{to_publishedDate}"' if to_publishedDate is not None else None,
                f'like_description: "{like_description}"' if like_description is not None else None,
                f'exact_pageCount: {exact_pageCount}' if exact_pageCount is not None else None,
                f'from_pageCount: {from_pageCount}' if from_pageCount is not None else None,
                f'to_pageCount: {to_pageCount}' if to_pageCount is not None else None,
                f'maturityRating: "{maturityRating}"' if maturityRating is not None else None,
                f'languages: {format_strings(languages)}' if languages is not None else None,
                f'authors: {format_strings(authors)}' if authors is not None else None,
                f'categories: {format_strings(categories)}' if categories is not None else None,
                f'limit: {limit}' if limit is not None else None,
                f'search: {format_strings(search)}' if search is not None else None,
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.GbooksDeep,
                post_data=HttpxPostData(
                    json={'query': build_query(type='query', name='booksDeep', args=args, fields=fields)}
                    )
                )
        
        @staticmethod
        def authors(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            names: Optional[List[str]] = None,
            like_names: Optional[str] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            search: Optional[List[str]] = None
        ) -> PostRequest[BooksResponse.Gauthors]:
            args = [
                f'names: {format_strings(names)}' if names is not None else None,
                f'like_names: "{like_names}"' if like_names is not None else None,
                f'offset: {offset}' if offset is not None else None,
                f'limit: {limit}' if limit is not None else None,
                f'search: {format_strings(search)}' if search is not None else None,
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.Gauthors,
                post_data=HttpxPostData(
                    json={'query': build_query(type='query', name='authors', args=args, fields=fields)}
                    )
            )
        
        @staticmethod
        def categories(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            names: Optional[List[str]] = None,
            like_names: Optional[str] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            search: Optional[List[str]] = None
        ) -> PostRequest[BooksResponse.Gcategories]:
            args = [
                f'names: {format_strings(names)}' if names is not None else None,
                f'like_names: "{like_names}"' if like_names is not None else None,
                f'offset: {offset}' if offset is not None else None,
                f'limit: {limit}' if limit is not None else None,
                f'search: {format_strings(search)}' if search is not None else None,
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.Gcategories,
                post_data=HttpxPostData(
                    json={'query': build_query(type='query', name='categories', args=args, fields=fields)}
                )
            )
        
        @staticmethod
        def reviews(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            ids: Optional[List[str]] = None,
            user_ids: Optional[List[str]] = None,
            stars: Optional[List[int]] = None,
            comments: Optional[List[str]] = None,
            like_comment: Optional[str] = None,
            actual: Optional[bool] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None
        ) -> PostRequest[BooksResponse.Greviews]:
            args = [
                f'ids: {format_strings(ids)}' if ids is not None else None,
                f'user_ids: {format_strings(user_ids)}' if user_ids is not None else None,
                f'stars: {stars}' if stars is not None else None,
                f'comments: {format_strings(comments)}' if comments is not None else None,
                f'like_comment: "{like_comment}"' if like_comment is not None else None,
                f'actual: {actual}' if actual is not None else None,
                f'offset: {offset}' if offset is not None else None,
                f'limit: {limit}' if limit is not None else None,
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.Greviews,
                post_data=HttpxPostData(
                    json={'query': build_query(type='query', name='reviews', args=args, fields=fields)}
                )
            )
        
        @staticmethod
        def reviewsDeep(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            ids: Optional[List[str]] = None,
            user_ids: Optional[List[str]] = None,
            books: Optional[List[str]] = None,
            from_stars: Optional[int] = None,
            before_stars: Optional[int] = None,
            like_comment: Optional[str] = None,
            actual: Optional[bool] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None
        ) -> PostRequest[BooksResponse.GreviewsDeep]:
            args = [
                f'ids: {format_strings(ids)}' if ids is not None else None,
                f'user_ids: {format_strings(user_ids)}' if user_ids is not None else None,
                f'books: {format_strings(books)}' if books is not None else None,
                f'from_stars: {from_stars}' if from_stars is not None else None,
                f'before_stars: {before_stars}' if before_stars is not None else None,
                f'like_comment: "{like_comment}"' if like_comment is not None else None,
                f'actual: {actual}' if actual is not None else None,
                f'offset: {offset}' if offset is not None else None,
                f'limit: {limit}' if limit is not None else None,
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.GreviewsDeep,
                post_data=HttpxPostData(
                    json={'query': build_query(type='mutation', name='reviewsDeep', args=args, fields=fields)}
                )
            )

        @staticmethod
        def createReview(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            user_id: str,
            book_id: str,
            stars: int,
            comment: Optional[str] = None
        ) -> PostRequest[BooksResponse.GcreateReview]:
            args = [
                f'user_id: "{user_id}"',
                f'book_id: "{book_id}"',
                f'stars: {stars}',
                f'comment: "{comment}"' if comment else None,
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.GcreateReview,
                post_data=HttpxPostData(
                    json={'query': build_query(type='mutation', name='createReview', args=args, fields=fields)}
                )
            )
        
        @staticmethod
        def updateReview(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            user_id: str,
            book_id: str,
            stars: int,
            comment: Optional[str] = None
        ) -> PostRequest[BooksResponse.GupdateReview]:
            args = [
                f'user_id: "{user_id}"',
                f'book_id: "{book_id}"',
                f'stars: {stars}',
                f'comment: "{comment}"' if comment else None,
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.GupdateReview,
                post_data=HttpxPostData(
                    json={'query': build_query(type='mutation', name='updateReview', args=args, fields=fields)}
                )
            )
        
        @staticmethod
        def deleteReview(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            user_id: str,
            book_id: str
        ) -> PostRequest[BooksResponse.GdeleteReview]:
            args = [
                f'user_id: "{user_id}"',
                f'book_id: "{book_id}"',
            ]
            return PostRequest(
                service=Service.BOOKS,
                path='graphql',
                response_type=BooksResponse.GdeleteReview,
                post_data=HttpxPostData(
                    json={'query': build_query(type='mutation', name='deleteReview', args=args, fields=fields)}
                )
            )
