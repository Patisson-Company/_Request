from typing import Generic, List, Optional, TypeAlias, TypeVar, Union

from pydantic import BaseModel
from patisson_request.errors import ErrorSchema
from patisson_request import jwt_tokens
from patisson_request.graphql.models import books_model as BooksGQL
from patisson_request.graphql.models import users_models as UsersGQL


GraphqlResponseType = TypeVar("GraphqlResponseType", bound=Union[
    '_GQLResponseFields.BooksService.books', '_GQLResponseFields.BooksService.booksDeep', 
    '_GQLResponseFields.BooksService.authors', '_GQLResponseFields.BooksService.categories', 
    '_GQLResponseFields.BooksService.reviews', '_GQLResponseFields.BooksService.reviewsDeep',
    '_GQLResponseFields.BooksService.createReview', '_GQLResponseFields.BooksService.updateReview',
    '_GQLResponseFields.BooksService.deleteReview'])

AccessTokenPayloadType = TypeVar("AccessTokenPayloadType", bound=Union[
    jwt_tokens.ClientAccessTokenPayload, jwt_tokens.ServiceAccessTokenPayload])

class _GQLResponseFields:
    
    class BooksService:
        
        class books(BaseModel):
            books: List[BooksGQL.Book]
            
        class booksDeep(BaseModel):
            books: List[BooksGQL.Book]
            
        class authors(BaseModel):
            authors: List[BooksGQL.Author]
            
        class categories(BaseModel):
            categories: List[BooksGQL.Category]
        
        class reviews(BaseModel):
            reviews: List[BooksGQL.Review]
            
        class reviewsDeep(BaseModel):
            reviews: List[BooksGQL.Review]

        class createReview(BaseModel):
            reviews: BooksGQL.ReviewResponse
        
        class updateReview(BaseModel):
            reviews: BooksGQL.ReviewResponse
        
        class deleteReview(BaseModel):
            reviews: BooksGQL.ReviewResponse


class GraphqlResponse(BaseModel, Generic[GraphqlResponseType]):
    data: GraphqlResponseType


class ErrorBodyResponse_4xx(BaseModel):
    detail: list[ErrorSchema] | str


class ErrorBodyResponse_5xx(BaseModel):
    error: str


class HealthCheckBodyResponse(BaseModel):
    status: str
    error: Optional[str] = None


class TokensSet(BaseModel):
        access_token: str
        refresh_token: str


class AuthenticationResponse:

    class Verify(BaseModel, Generic[AccessTokenPayloadType]):
        is_verify: bool
        payload: Optional[AccessTokenPayloadType]
        error: Optional[ErrorSchema] = None

class BooksResponse:
        
    class Gbooks(GraphqlResponse[_GQLResponseFields.BooksService.books]):
        ''''''
        
    class GbooksDeep(GraphqlResponse[_GQLResponseFields.BooksService.booksDeep]):
        ''''''
        
    class Gauthors(GraphqlResponse[_GQLResponseFields.BooksService.authors]):
        ''''''
        
    class Gcategories(GraphqlResponse[_GQLResponseFields.BooksService.categories]):
        ''''''
    
    class Greviews(GraphqlResponse[_GQLResponseFields.BooksService.reviews]):
        ''''''
        
    class GreviewsDeep(GraphqlResponse[_GQLResponseFields.BooksService.reviewsDeep]):
        ''''''

    class GcreateReview(GraphqlResponse[_GQLResponseFields.BooksService.createReview]):
        ''''''
    
    class GupdateReview(GraphqlResponse[_GQLResponseFields.BooksService.updateReview]):
        ''''''
    
    class GdeleteReview(GraphqlResponse[_GQLResponseFields.BooksService.deleteReview]):
        ''''''


ResponseBody: TypeAlias = (
    ErrorBodyResponse_4xx | ErrorBodyResponse_5xx
    | HealthCheckBodyResponse | GraphqlResponse
    | jwt_tokens.RefreshTokenPayload 
    | AuthenticationResponse.Verify 
    | TokensSet   
)

ResponseType = TypeVar("ResponseType", bound=ResponseBody)