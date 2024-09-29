from typing import Generic, List, Optional, TypeAlias, TypeVar, Union

from patisson_errors.core import ErrorSchema
from patisson_tokens.jwt import schemas as token
from pydantic import BaseModel

from patisson_request.graphql.models import books_model as BooksGQL
from patisson_request.graphql.models import users_models as UsersGQL

GraphqlResponseType = TypeVar("GraphqlResponseType")

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


class ErrorBodyResponse(BaseModel):
    detail: list[ErrorSchema] | str


class HealthCheckBodyResponse(BaseModel):
    status: str
    error: Optional[str] = None


class AuthenticationResponse:
    
    class TokensSet(BaseModel):
        access_token: str
        refresh_token: str


class BooksResponse:
        
    class books(GraphqlResponse[_GQLResponseFields.BooksService.books]):
        ''''''
        
    class booksDeep(GraphqlResponse[_GQLResponseFields.BooksService.booksDeep]):
        ''''''
        
    class authors(GraphqlResponse[_GQLResponseFields.BooksService.authors]):
        ''''''
        
    class categories(GraphqlResponse[_GQLResponseFields.BooksService.categories]):
        ''''''
    
    class reviews(GraphqlResponse[_GQLResponseFields.BooksService.reviews]):
        ''''''
        
    class reviewsDeep(GraphqlResponse[_GQLResponseFields.BooksService.reviewsDeep]):
        ''''''

    class createReview(GraphqlResponse[_GQLResponseFields.BooksService.createReview]):
        ''''''
    
    class updateReview(GraphqlResponse[_GQLResponseFields.BooksService.updateReview]):
        ''''''
    
    class deleteReview(GraphqlResponse[_GQLResponseFields.BooksService.deleteReview]):
        ''''''


ResponseBody: TypeAlias = (
    ErrorBodyResponse | HealthCheckBodyResponse 
    | token.ClientPayload | token.ServicePayload
    | token.RefreshPayload | AuthenticationResponse.TokensSet
    | GraphqlResponse
)

ResponseType = TypeVar("ResponseType", bound=ResponseBody)