from enum import Enum

class Service(Enum):
    AUTHENTICATION = 'authentication'
    BOOKS = 'books'
    USERS = "users"
    FORUM = "forum"
    INTERNAL_MEDIA = "internal_media"
    API_GATEWAY = "api_gateway"