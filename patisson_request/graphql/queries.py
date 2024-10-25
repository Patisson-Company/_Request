from typing import List, Optional, Sequence, Union
from patisson_request.graphql.models.books_model import *
from patisson_request.graphql.models.users_models import *
from patisson_request.types import *

__all__ = [
    'QBook',
    'QAuthor',
    'QCategory',
    'QReview',
    'QError',
    'QReviewResponse',
    'QUser'
]

ID: TypeAlias = str

class QBook:
    id = 'id'
    google_id = 'google_id'
    title = 'title'
    publisher = 'publisher'
    publishedDate = 'publishedDate'
    description = 'description'
    pageCount = 'pageCount'
    maturityRating = 'maturityRating'
    smallThumbnail = 'smallThumbnail'
    thumbnail = 'thumbnail'
    language = 'language'
    authors = 'authors'
    categories = 'categories'


class QAuthor:
    name = 'name'
    books = 'books'


class QCategory:
    name = 'name'
    books = 'books'


class QReview:
    id = 'id'
    user_id = 'user_id'
    book = 'book'
    stars = 'stars'
    comment = 'comment'
    actual = 'actual'


class QError:
    error = 'error'
    extra = 'extra'


class QReviewResponse:
    success = 'success'
    errors = 'errors'
    
    
class QUser:
    id = 'id'
    username = 'username'
    firstName = 'firstName'
    lastName = 'lastName'
    avatar = 'avatar'
    about = 'about'
    role = 'role'
    
    
def build_query(type: str, name: str, args: Sequence[Optional[str]], 
                fields: Sequence[GraphqlField | NestedGraphqlFields]) -> str:
    query_args = ', '.join(filter(None, args))
    return f'{type} {{ {name}{'(' + query_args+ ')' if query_args != "" else ""} {{ {build_query_fields(fields)} }} }}'

def build_query_fields(fields: Sequence[GraphqlField | NestedGraphqlFields]) -> str:
    query = ''
    for block in fields:
        if isinstance(block, GraphqlField):
            query += block + ' '
        else:  # NestedGraphqlFields
            for key, value in block.items():
                query += f"{key}{{{build_query_fields(value)}}}"
    return query

def format_strings(sequence: Sequence[str]) -> str:
    return '[' + ', '.join(f'"{item}"' for item in sequence) + ']'
