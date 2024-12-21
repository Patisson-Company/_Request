from typing import Literal, Optional, TypeAlias

from pydantic import Field

from patisson_request.graphql.models.base import EmptyField, GraphQLBaseModel

Boolean: TypeAlias = bool
ID: TypeAlias = str
String: TypeAlias = str


class User(GraphQLBaseModel):
    id: ID = EmptyField()  # type: ignore[reportAssignmentType]
    role: String = EmptyField()  # type: ignore[reportAssignmentType]
    username: String = EmptyField()  # type: ignore[reportAssignmentType]
    about: Optional["String"] = EmptyField()  # type: ignore[reportAssignmentType]
    avatar: Optional["String"] = EmptyField()  # type: ignore[reportAssignmentType]
    firstName: Optional["String"] = EmptyField()  # type: ignore[reportAssignmentType]
    lastName: Optional["String"] = EmptyField()  # type: ignore[reportAssignmentType]
    typename__: Literal["User"] = Field(default="User", alias="__typename")


class Library(GraphQLBaseModel):
    id: ID = EmptyField()  # type: ignore[reportAssignmentType]
    user_id: String = EmptyField()  # type: ignore[reportAssignmentType]
    book_id: String = EmptyField()  # type: ignore[reportAssignmentType]
    status: String = EmptyField()  # type: ignore[reportAssignmentType]
    typename__: Literal["Library"] = Field(default="Library", alias="__typename")
