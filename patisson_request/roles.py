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
        raise AttributeError(f"Cannot modify immutable attribute")

    def __delattr__(self, name):
        raise AttributeError(f"Cannot delete attribute from frozen class")
        
    
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
            create_lib = True,
            create_ban = True,
            use_chat=True
        )
    )
    MEMBER = Role[ClientPermissions](
        "MEMBER",
        ClientPermissions(
            create_lib = True,
            create_ban = False,
            use_chat=True
            )
        )
    ADMIN = Role[ClientPermissions](
        "ADMIN",
        ClientPermissions(
            create_lib = True,
            create_ban = True,
            use_chat=True
            )
        )
    OWNER = Role[ClientPermissions](
        "OWNER",
        ClientPermissions(
            create_lib = True,
            create_ban = True,
            use_chat=True
            )
        )


ServiceRole = _ServiceRole()
ClientRole = _ClientRole()