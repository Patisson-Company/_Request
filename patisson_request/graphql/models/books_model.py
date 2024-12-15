from typing import Literal, Optional
from pydantic import Field

from patisson_request.graphql.models.base import EmptyField, GraphQLBaseModel

Boolean = bool
ID = str
Int = int
String = str


class Author(GraphQLBaseModel):
    name: String = EmptyField()  # type: ignore[reportAssignmentType]
    books: Optional[list[Optional['Book']]] = EmptyField()  # type: ignore[reportAssignmentType]
    typename__: Literal["Author"] = Field(default="Author", alias="__typename")


class Book(GraphQLBaseModel):
    google_id: String = EmptyField()  # type: ignore[reportAssignmentType]
    id: String = EmptyField()  # type: ignore[reportAssignmentType]
    title: String = EmptyField()  # type: ignore[reportAssignmentType]
    authors: Optional[list[Optional['Author']]] = EmptyField()  # type: ignore[reportAssignmentType]
    categories: Optional[list[Optional['Category']]] = EmptyField()  # type: ignore[reportAssignmentType]
    description: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    language: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    maturityRating: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    pageCount: Optional[Int] = EmptyField()  # type: ignore[reportAssignmentType]
    publishedDate: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    publisher: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    smallThumbnail: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    thumbnail: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    typename__: Literal["Book"] = Field(default="Book", alias="__typename")


class Category(GraphQLBaseModel):
    name: String = EmptyField()  # type: ignore[reportAssignmentType]
    books: Optional[list[Optional['Book']]] = EmptyField()  # type: ignore[reportAssignmentType]
    typename__: Literal["Category"] = Field(default="Category", alias="__typename")


class Error(GraphQLBaseModel):
    error: String = EmptyField()  # type: ignore[reportAssignmentType]
    extra: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    typename__: Literal["Error"] = Field(default="Error", alias="__typename")


class Review(GraphQLBaseModel):
    actual: Boolean = EmptyField()  # type: ignore[reportAssignmentType]
    book: Book = EmptyField()  # type: ignore[reportAssignmentType]
    id: ID = EmptyField()  # type: ignore[reportAssignmentType]
    stars: Int = EmptyField()  # type: ignore[reportAssignmentType]
    user_id: String = EmptyField()  # type: ignore[reportAssignmentType]
    comment: Optional[String] = EmptyField()  # type: ignore[reportAssignmentType]
    typename__: Literal["Review"] = Field(default="Review", alias="__typename")


class ReviewResponse(GraphQLBaseModel):
    success: Boolean = EmptyField()  # type: ignore[reportAssignmentType]
    errors: Optional[list[Optional['Error']]] = EmptyField()  # type: ignore[reportAssignmentType]
    typename__: Literal["ReviewResponse"] = Field(default="ReviewResponse", alias="__typename")


Author.update_forward_refs()
Book.update_forward_refs()
Category.update_forward_refs()
Error.update_forward_refs()
Review.update_forward_refs()
ReviewResponse.update_forward_refs()
