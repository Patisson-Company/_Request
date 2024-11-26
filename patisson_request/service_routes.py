from datetime import datetime
from typing import Callable, List, Optional, Sequence, Union

from patisson_request import jwt_tokens
from patisson_request.graphql.queries import build_query, format_strings
from patisson_request.roles import ClientPermissions, Role
from patisson_request.service_requests import (AuthenticationRequest,
                                               GetRequest, HttpxPostData,
                                               PostRequest, UsersRequest)
from patisson_request.service_responses import (AuthenticationResponse,
                                                BooksResponse,
                                                HealthCheckBodyResponse,
                                                IntertnalMediaResponse,
                                                SuccessResponse,
                                                TokensSetResponse,
                                                UsersResponse,
                                                VerifyUserResponse)
from patisson_request.services import Service
from patisson_request.types import (GraphqlField, NestedGraphqlFields,
                                    RequestFiles, Seconds, Token)


def url_params(**kwargs) -> str:
    query = ''
    for kwarg in kwargs:
        if kwarg: 
            query += f'{kwarg}={kwargs[kwarg]}&'
    return query


class AuthenticationRoute:
    
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
                    def create(client_id: str, client_role: Role[ClientPermissions],
                            expire_in: Optional[Seconds] = None
                            ) -> PostRequest[TokensSetResponse]:
                        path = 'api/v1/client/jwt/create'
                        return PostRequest(
                            service=Service.AUTHENTICATION,
                            path=path,
                            post_data=HttpxPostData(
                                json=AuthenticationRequest.CreateClient(
                                    client_id=client_id,
                                    client_role=client_role.name,
                                    expire_in=expire_in
                                )),
                            response_type=TokensSetResponse
                        )
                    
                    @staticmethod
                    def verify(client_access_token: Token
                            ) -> PostRequest[
                                AuthenticationResponse.Verify[
                                    jwt_tokens.ClientAccessTokenPayload]]:
                        path = 'api/v1/client/jwt/verify'
                        return PostRequest(
                            service=Service.AUTHENTICATION,
                            path=path,
                            post_data=HttpxPostData(
                                json=AuthenticationRequest.Verify(
                                    access_token=client_access_token
                                )),
                            response_type=AuthenticationResponse.Verify
                        )
                    
                    @staticmethod
                    def update(client_access_token: Token,
                            client_refresh_token: Token,
                            expire_in: Optional[Seconds] = None
                            ) -> PostRequest[TokensSetResponse]:
                        path = 'api/v1/client/jwt/update'
                        return PostRequest(
                            service=Service.AUTHENTICATION,
                            path=path,
                            post_data=HttpxPostData(
                                json=AuthenticationRequest.UpdateClient(
                                    client_access_token=client_access_token,
                                    client_refresh_token=client_refresh_token,
                                    expire_in=expire_in
                                )),
                            response_type=TokensSetResponse
                        )
            
            class service: 
                class jwt:
                    
                    @staticmethod
                    def create(login: str, password: str
                            ) -> PostRequest[TokensSetResponse]:
                        path = 'api/v1/service/jwt/create'
                        return PostRequest(
                            service=Service.AUTHENTICATION,
                            path=path,
                            post_data=HttpxPostData(
                                json=AuthenticationRequest.CreateService(
                                    login=login,
                                    password=password
                                )),
                            response_type=TokensSetResponse
                        )
                    
                    @staticmethod
                    def verify(verified_service_jwt: Token
                            ) -> PostRequest[
                                AuthenticationResponse.Verify[
                                    jwt_tokens.ServiceAccessTokenPayload]]:
                        path = 'api/v1/service/jwt/verify'
                        return PostRequest(
                            service=Service.AUTHENTICATION,
                            path=path,
                            post_data=HttpxPostData(
                                json=AuthenticationRequest.Verify(
                                    access_token=verified_service_jwt
                                )),
                            response_type=AuthenticationResponse.Verify
                        )
                    
                    @staticmethod
                    def update(refresh_token: Token
                            ) -> PostRequest[TokensSetResponse]:
                        path = 'api/v1/service/jwt/update'
                        return PostRequest(
                            service=Service.AUTHENTICATION,
                            path=path,
                            post_data=HttpxPostData(
                                json=AuthenticationRequest.UpdateService(
                                    refresh_token=refresh_token
                                )),
                            response_type=TokensSetResponse
                        )


class BooksRoute:
    
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
                    ),
                is_graphql=True
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
                    ),
                is_graphql=True
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
                    ),
                is_graphql=True
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
                ),
                is_graphql=True
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
                ),
                is_graphql=True
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
                ),
                is_graphql=True
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
                ),
                is_graphql=True
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
                ),
                is_graphql=True
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
                ),
                is_graphql=True
            )


class UsersRoute:
    
    @staticmethod
    def health() -> GetRequest[HealthCheckBodyResponse]:
        return GetRequest(
            service=Service.USERS,
            path='health',
            response_type=HealthCheckBodyResponse
        )
    
    class graphql:

        @staticmethod
        def users(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            ids: Optional[List[str]] = None,
            usernames: Optional[List[str]] = None,
            first_names: Optional[List[str]] = None,
            last_names: Optional[List[str]] = None,
            roles: Optional[List[str]] = None,
            is_banned: Optional[bool] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None
        ) -> PostRequest[UsersResponse.Gusers]:
            args = [
                f'ids: {format_strings(ids)}' if ids is not None else None,
                f'usernames: {format_strings(usernames)}' if usernames is not None else None,
                f'first_names: {format_strings(first_names)}' if first_names is not None else None,
                f'last_names: {format_strings(last_names)}' if last_names is not None else None,
                f'roles: {format_strings(roles)}' if roles is not None else None,
                f'is_banned: {str(is_banned).lower()}' if is_banned is not None else None,
                f'offset: {offset}' if offset is not None else None,
                f'limit: {limit}' if limit is not None else None,
            ]
            return PostRequest(
                service=Service.USERS,
                path='graphql',
                response_type=UsersResponse.Gusers,
                post_data=HttpxPostData(
                    json={'query': build_query(type='query', name='users', args=args, fields=fields)}
                    ),
                is_graphql=True
            )
            
        @staticmethod
        def libraries(
            fields: Sequence[Union[GraphqlField, NestedGraphqlFields]],
            ids: Optional[List[str]] = None,
            user_ids: Optional[List[str]] = None,
            book_ids: Optional[List[str]] = None,
            statuses: Optional[List[str]] = None
        ) -> PostRequest[UsersResponse.Glibraries]:
            args = [
                f'ids: {format_strings(ids)}' if ids is not None else None,
                f'user_ids: {format_strings(user_ids)}' if user_ids is not None else None,
                f'book_ids: {format_strings(book_ids)}' if book_ids is not None else None,
                f'statuses: {format_strings(statuses)}' if statuses is not None else None,
            ]
            return PostRequest(
                service=Service.USERS,
                path='graphql',
                response_type=UsersResponse.Glibraries,
                post_data=HttpxPostData(
                    json={'query': build_query(type='query', name='libraries', args=args, fields=fields)}
                ),
                is_graphql=True
            )
    
    class api:
        
        class v1:
            
            @staticmethod
            def create_user(
                username: str, password: str,
                first_name: Optional[str] = None,
                last_name: Optional[str] = None,
                avatar: Optional[str] = None,
                about: Optional[str] = None,
                expire_in: Optional[Seconds] = None
                ) -> PostRequest[TokensSetResponse]:
                path = 'api/v1/create-user'
                return PostRequest(
                    service=Service.USERS,
                    path=path,
                    post_data=HttpxPostData(
                        json=UsersRequest.CreateUser(
                            username=username,
                            password=password,
                            first_name=first_name,
                            last_name=last_name,
                            avatar=avatar,
                            about=about,
                            expire_in=expire_in
                        )),
                    response_type=TokensSetResponse
                )
        
            @staticmethod
            def create_library(
                book_id: str, user_id: str, status: int
                ) -> PostRequest[SuccessResponse]:
                path = 'api/v1/create-library'
                return PostRequest(
                    service=Service.USERS,
                    path=path,
                    post_data=HttpxPostData(
                        json=UsersRequest.CreateLibrary(
                            book_id=book_id,
                            user_id=user_id,
                            status=status
                        )),
                    response_type=SuccessResponse
                )
                
            @staticmethod
            def create_ban(
                user_id: str, reason: int, 
                comment: str, end_date: datetime
                ) -> PostRequest[SuccessResponse]:
                path = 'api/v1/create-ban'
                return PostRequest(
                    service=Service.USERS,
                    path=path,
                    post_data=HttpxPostData(
                        json=UsersRequest.CreateBan(
                            user_id=user_id,
                            reason=reason,
                            comment=comment,
                            end_date=end_date,
                        )),
                    response_type=SuccessResponse
                )
                
            @staticmethod
            def verify_user(
                access_token: str
            ) -> PostRequest[VerifyUserResponse]:
                path = 'api/v1/verify-user'
                return PostRequest(
                    service=Service.USERS,
                    path=path,
                    post_data=HttpxPostData(
                        json=UsersRequest.VerifyUser(
                            access_token=access_token
                        )
                    ),
                    response_type=VerifyUserResponse
                )
                
            @staticmethod
            def update_user(
                refresh_token: str
            ) -> PostRequest[TokensSetResponse]:
                path = 'api/v1/update-user'
                return PostRequest(
                    service=Service.USERS,
                    path=path,
                    post_data=HttpxPostData(
                        json=UsersRequest.UpdateUser(
                            refresh_token=refresh_token
                        )
                    ),
                    response_type=TokensSetResponse
                )
                

class InternalMediaRoute:
    
    @staticmethod
    def health() -> GetRequest[HealthCheckBodyResponse]:
        return GetRequest(
            service=Service.INTERNAL_MEDIA,
            path='health',
            response_type=HealthCheckBodyResponse
        )
    
    class api:
        
        class v1:
            
            @staticmethod
            def upload(
                file: bytes
            ) -> PostRequest[IntertnalMediaResponse.FileID]:
                path = 'api/v1/upload'
                return PostRequest(
                    service=Service.INTERNAL_MEDIA,
                    path=path,
                    post_data=HttpxPostData(
                        files={'file': file}
                    ),  # type: ignore[]
                    response_type=IntertnalMediaResponse.FileID
                )
    
        
        
USERS_VERIFY_ROUTE: dict[
    Service, Callable[..., PostRequest[VerifyUserResponse]]] = {
    Service.USERS: UsersRoute.api.v1.verify_user
}