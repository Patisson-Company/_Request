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
    
    def __call__(self, role: str) -> Role[Permissions]:
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
    AUTHENTICATION = Role[ServicePermissions](
        "AUTHENTICATION", 
        ServicePermissions(
            media_access=False,
            users_auth=True,
            user_reg=False,
            forum_access=False
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
    GUEST = Role[ClientPermissions](
        "GUEST",
        ClientPermissions(
            create_lib = False,
            create_ban = False,
            use_chat=False
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