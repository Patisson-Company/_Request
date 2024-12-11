from typing import Optional, Sequence

from patisson_request.types import GraphqlField, NestedGraphqlFields

__all__ = [
    'QBook',
    'QAuthor',
    'QCategory',
    'QReview',
    'QError',
    'QReviewResponse',
    'QUser'
]


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
    """
    Constructs a GraphQL query string.

    Args:
        type (str): The query type (e.g., 'query' or 'mutation').
        name (str): The name of the GraphQL operation.
        args (Sequence[Optional[str]]): A sequence of arguments for the query (optional).
        fields (Sequence[GraphqlField | NestedGraphqlFields]): A sequence of fields to be queried, which can be
            simple fields (GraphqlField) or nested fields (NestedGraphqlFields).

    Returns:
        str: The complete GraphQL query string.
    """
    query_args = ', '.join(filter(None, args))
    return f'{type} {{ {name}{'(' + query_args+ ')' if query_args != "" else ""} {{ {build_query_fields(fields)} }} }}'

def build_query_fields(fields: Sequence[GraphqlField | NestedGraphqlFields]) -> str:
    """
    Constructs the fields portion of a GraphQL query, handling both simple and nested fields.

    Args:
        fields (Sequence[GraphqlField | NestedGraphqlFields]): A sequence of fields, which can be simple 
            fields (GraphqlField) or nested fields (NestedGraphqlFields).

    Returns:
        str: The fields portion of the GraphQL query string.
    """
    query = ''
    for block in fields:
        if isinstance(block, GraphqlField):
            query += block + ' '
        else:  # NestedGraphqlFields
            for key, value in block.items():
                query += f"{key}{{{build_query_fields(value)}}}"
    return query

def format_strings(sequence: Sequence[str]) -> str:
    """
    Formats a sequence of strings into a GraphQL array format.

    Args:
        sequence (Sequence[str]): A sequence of strings to be formatted.

    Returns:
        str: The formatted GraphQL array.
    """
    return '[' + ', '.join(f'"{item}"' for item in sequence) + ']'
