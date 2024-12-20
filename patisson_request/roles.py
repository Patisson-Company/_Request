"""
This module defines roles with associated permissions for different entities within the system,
including service and client roles.

The roles are designed to be immutable and provide strict validation of permissions. Each role corresponds
to a set of permissions that govern the access and functionality for a particular entity.

Key Concepts:
- **ServicePermissions**: Defines a set of permissions related to the service layer, such as media access,
    user authentication, user registration, and forum access.
- **ClientPermissions**: Defines a set of permissions for client operations, such as creating libraries,
    banning users, and using chat.
- **Role**: A class that encapsulates a role name and its associated permissions. It is generic and can
    represent either `ServicePermissions` or `ClientPermissions`.
- **_EntityRoles**: A base class for immutable role enumerations, ensuring that roles cannot be modified
    after creation. Provides a lookup method for retrieving role objects by name.
- **_ServiceRole and _ClientRole**: Concrete implementations of `_EntityRoles` for service and client roles,
    respectively. These classes define a set of predefined roles with their associated permissions.
- **Role Lookup**: Roles can be accessed via the class (e.g., `ServiceRole._TEST`) or by calling the class
    with the role name (e.g., `ServiceRole('SERVES_USERS')`).

Classes:
    - `ServicePermissions`: A Pydantic data class that defines permissions for services.
    - `ClientPermissions`: A Pydantic data class that defines permissions for clients.
    - `Role`: A generic class representing a role associated with a set of permissions.
    - `_EntityRoles`: A generic base class for immutable role enumerations, ensuring role immutability and
        providing lookup functionality.
    - `_ServiceRole`: A concrete class for service roles, defining common roles such as `_TEST`, `MINIMUM`,
        and `MEDIA_ACCESS`.
    - `_ClientRole`: A concrete class for client roles, defining common roles such as `_TEST`, `MEMBER`,
        `ADMIN`, and `OWNER`.

Usage:
    - To define new roles or to retrieve existing roles, you can instantiate or call the appropriate role
        enumeration class (`ServiceRole` or `ClientRole`).
    - Roles can be retrieved by calling the role class with the role name, e.g.,
        `ServiceRole('MEDIA_ACCESS')`.
    - The permissions associated with each role can be accessed through the `permissions` property of
        the `Role` class.

Example:
    - To retrieve the `MEDIA_ACCESS` role for services:
      ```python
      media_access_role = ServiceRole('MEDIA_ACCESS')
      print(media_access_role.permissions)
      ```
    - To retrieve the `ADMIN` role for clients:
      ```python
      admin_role = ClientRole('ADMIN')
      print(admin_role.permissions)
      ```
"""

from abc import ABC
from dataclasses import dataclass
from functools import cached_property
from typing import Generic, TypeVar, Union

Permissions = TypeVar("Permissions", bound=Union['ServicePermissions', 'ClientPermissions'])


@dataclass(frozen=True, kw_only=True)
class ServicePermissions:
    users_auth: bool
    user_reg: bool
    media_access: bool
    forum_access: bool


@dataclass(frozen=True, kw_only=True)
class ClientPermissions:
    create_lib: bool
    create_ban: bool
    use_chat: bool


class Role(Generic[Permissions]):
    """
    A class representing a role that is associated with a set of permissions.
    The role encapsulates the name of the role and the corresponding permissions, which can be either
    service-related or client-related permissions.

    Args:
        name (str): The name of the role (e.g., 'admin', 'user').
        permissions (Permissions): The set of permissions associated with the role.
                                   This is a generic type that can be either `ServicePermissions`
                                   or `ClientPermissions`.

    Methods:
        permissions (cached_property): Returns the permissions associated with the role.
        name (cached_property): Returns the name of the role.
        __str__ (): Returns the string representation of the role (its name).
        __repr__ (): Returns the string representation of the role (its name) for debugging purposes.
    """

    def __init__(self, name: str, permissions: Permissions):
        self.__name = name
        self.__permissions = permissions

    @cached_property
    def permissions(self) -> Permissions:
        return self.__permissions

    @cached_property
    def name(self) -> str:
        return self.__name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class _EntityRoles(ABC, Generic[Permissions]):
    """
    Represents an immutable role enumeration with additional functionality.

    This class acts as an enumeration for roles, with support for generic
    permissions. It provides role lookup via the `__call__` method and ensures
    immutability by overriding attribute modification methods.
    """

    def __call__(self, role: str) -> 'Role[Permissions]':
        """
        Retrieves the role object corresponding to the provided role name.

        Args:
            role (str): The name of the role to retrieve.

        Returns:
            Role[Permissions]: The role object corresponding to the given name.

        Raises:
            ValueError: If the role name is not defined in the class.
        """
        role_attr = getattr(self.__class__, role, None)
        if role_attr is None:
            raise ValueError('incorrect role name')
        return role_attr

    def __setattr__(self, name, value):
        raise AttributeError("Cannot modify immutable attribute")

    def __delattr__(self, name):
        raise AttributeError("Cannot delete attribute from frozen class")


class _ServiceRole(_EntityRoles[ServicePermissions]):
    _TEST = Role[ServicePermissions](
        "_TEST",
        ServicePermissions(
            media_access=True,
            users_auth=True,
            user_reg=True,
            forum_access=True
        )
    )
    MINIMUM = Role[ServicePermissions](
        "MINIMUM",
        ServicePermissions(
            media_access=False,
            users_auth=False,
            user_reg=False,
            forum_access=False
            )
        )
    SERVES_USERS = Role[ServicePermissions](
        "SERVES_USERS",
        ServicePermissions(
            media_access=True,
            users_auth=True,
            user_reg=True,
            forum_access=False
            )
        )
    MEDIA_ACCESS = Role[ServicePermissions](
        "MEDIA_ACCESS",
        ServicePermissions(
            media_access=True,
            users_auth=False,
            user_reg=False,
            forum_access=False
            )
        )
    PROXY = Role[ServicePermissions](
        "PROXY",
        ServicePermissions(
            media_access=True,
            users_auth=False,
            user_reg=True,
            forum_access=True
            )
        )


class _ClientRole(_EntityRoles[ClientPermissions]):
    _TEST = Role[ClientPermissions](
        "_TEST",
        ClientPermissions(
            create_lib=True,
            create_ban=True,
            use_chat=True
        )
    )
    MEMBER = Role[ClientPermissions](
        "MEMBER",
        ClientPermissions(
            create_lib=True,
            create_ban=False,
            use_chat=True
            )
        )
    ADMIN = Role[ClientPermissions](
        "ADMIN",
        ClientPermissions(
            create_lib=True,
            create_ban=True,
            use_chat=True
            )
        )
    OWNER = Role[ClientPermissions](
        "OWNER",
        ClientPermissions(
            create_lib=True,
            create_ban=True,
            use_chat=True
            )
        )


ServiceRole = _ServiceRole()
ClientRole = _ClientRole()
