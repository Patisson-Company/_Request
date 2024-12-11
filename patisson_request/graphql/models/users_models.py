import typing as _t

from pydantic import Field

from patisson_request.graphql.models.base import EmptyField, GraphQLBaseModel

Boolean = str
ID = str
String = str


class User(GraphQLBaseModel):
    id: ID | EmptyField = EmptyField()
    role: String | EmptyField = EmptyField()
    username: String | EmptyField = EmptyField()
    about: _t.Optional['String'] | EmptyField = EmptyField()
    avatar: _t.Optional['String'] | EmptyField = EmptyField()
    firstName: _t.Optional['String'] | EmptyField = EmptyField()
    lastName: _t.Optional['String'] | EmptyField = EmptyField()
    typename__: _t.Literal["User"] = Field(default="User", alias="__typename")


class Library(GraphQLBaseModel):
    id: ID | EmptyField = EmptyField()
    user_id: String | EmptyField = EmptyField()
    book_id: String | EmptyField = EmptyField()
    status: String | EmptyField = EmptyField()
    typename__: _t.Literal["Library"] = Field(default="Library", alias="__typename")
    
    
User.update_forward_refs()
Library.update_forward_refs()
