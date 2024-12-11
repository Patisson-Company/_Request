import typing as _t

from pydantic import Field

from patisson_request.graphql.models.base import EmptyField, GraphQLBaseModel

Boolean = str
ID = str
Int = str
String = str


class Author(GraphQLBaseModel):
    name: 'String' = Field(default=EmptyField())
    books: _t.Optional[_t.List[_t.Optional['Book']]] = Field(default=EmptyField())
    typename__: _t.Literal["Author"] = Field(default="Author", alias="__typename")


class Book(GraphQLBaseModel):
    google_id: String | EmptyField = EmptyField()
    id: String | EmptyField = EmptyField()
    title: String | EmptyField = EmptyField()
    authors: _t.Optional[_t.List[_t.Optional['Author']]] | EmptyField = EmptyField()
    categories: _t.Optional[_t.List[_t.Optional['Category']]] | EmptyField = EmptyField()
    description: _t.Optional['String'] | EmptyField = EmptyField()
    language: _t.Optional['String'] | EmptyField = EmptyField()
    maturityRating: _t.Optional['String'] | EmptyField = EmptyField()
    pageCount: _t.Optional['Int'] | EmptyField = EmptyField()
    publishedDate: _t.Optional['String'] | EmptyField = EmptyField()
    publisher: _t.Optional['String'] | EmptyField = EmptyField()
    smallThumbnail: _t.Optional['String'] | EmptyField = EmptyField()
    thumbnail: _t.Optional['String'] | EmptyField = EmptyField()
    typename__: _t.Literal["Book"] = Field(default="Book", alias="__typename")


class Category(GraphQLBaseModel):
    name: 'String' = Field(default=EmptyField())
    books: _t.Optional[_t.List[_t.Optional['Book']]] = Field(default=EmptyField())
    typename__: _t.Literal["Category"] = Field(default="Category", alias="__typename")


class Error(GraphQLBaseModel):
    """
    An Object type
    See https://graphql.org/learn/schema/#object-types-and-fields
    """
    error: String | EmptyField = EmptyField()
    extra: _t.Optional['String'] | EmptyField = EmptyField()
    typename__: _t.Literal["Error"] = Field(default="Error", alias="__typename")


class Review(GraphQLBaseModel):
    """
    An Object type
    See https://graphql.org/learn/schema/#object-types-and-fields
    """
    actual: Boolean | EmptyField = EmptyField()
    book: Book | EmptyField = EmptyField()
    id: ID | EmptyField = EmptyField()
    stars: Int | EmptyField = EmptyField()
    user_id: String | EmptyField = EmptyField()
    comment: _t.Optional['String'] | EmptyField = EmptyField()
    typename__: _t.Literal["Review"] = Field(default="Review", alias="__typename")


class ReviewResponse(GraphQLBaseModel):
    """
    An Object type
    See https://graphql.org/learn/schema/#object-types-and-fields
    """
    success: Boolean | EmptyField = EmptyField()
    errors: _t.Optional[_t.List[_t.Optional['Error']]] | EmptyField = EmptyField()
    typename__: _t.Literal["ReviewResponse"] = Field(default="ReviewResponse", alias="__typename")


Author.update_forward_refs()
Book.update_forward_refs()
Category.update_forward_refs()
Error.update_forward_refs()
Review.update_forward_refs()
ReviewResponse.update_forward_refs()
