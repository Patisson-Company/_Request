from abc import ABC
from dataclasses import dataclass
from functools import cached_property
from typing import Generic, TypeVar, Union

Permissions = TypeVar("Permissions", bound=Union['ServicePermissions', 'ClientPermissions'])


# Permissions

@dataclass(frozen=True, kw_only=True)    
class ServicePermissions:
    users_auth: bool
    

@dataclass(frozen=True, kw_only=True)    
class ClientPermissions:
    pass


# Role
    
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
    
    
# EntityRoles

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
    MINIMUM = Role[ServicePermissions](
        "MINIMUM", 
        ServicePermissions(
            users_auth=False
            )
        )
    SERVES_USERS = Role[ServicePermissions](
        "SERVES_USERS",
        ServicePermissions(
            users_auth=True
            )
        )
    AUTHENTICATION = Role[ServicePermissions](
        "AUTHENTICATION", 
        ServicePermissions(
            users_auth=True
            )
        )
    
    
class _ClientRole(_EntityRoles[ServicePermissions]):
    GUEST = Role[ClientPermissions](
        "GUEST",
        ClientPermissions(
            
            )
        )
    MEMBER = Role[ClientPermissions](
        "MEMBER",
        ClientPermissions(
            
            )
        )
    ADMIN = Role[ClientPermissions](
        "ADMIN",
        ClientPermissions(
            
            )
        )
    OWNER = Role[ClientPermissions](
        "OWNER",
        ClientPermissions(
            
            )
        )


ServiceRole = _ServiceRole()
ClientRole = _ClientRole()