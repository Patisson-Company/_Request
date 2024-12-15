"""
This module defines the `Service` enum, which represents various microservices in a distributed system.
Each enum member corresponds to a specific service by its unique identifier.

Classes:
    - Service: Enumeration of microservices with their respective service names.
"""

from enum import Enum

class Service(Enum):
    _TEST = '_test'
    AUTHENTICATION = 'authentication'
    BOOKS = 'books'
    USERS = "users"
    FORUM = "forum"
    INTERNAL_MEDIA = "internal_media"
    API_GATEWAY = "api_gateway"