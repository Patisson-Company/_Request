from patisson_request.roles import (ClientPermissions, ClientRole, Role,
                                    ServicePermissions, ServiceRole)


def test_client_role():
    role = ClientRole._TEST
    assert isinstance(role, Role)
    assert isinstance(role.name, str)
    assert isinstance(role.permissions, ClientPermissions)
    assert isinstance(role.permissions.create_ban, bool)


def test_service_role():
    role = ServiceRole._TEST
    assert isinstance(role, Role)
    assert isinstance(role.name, str)
    assert isinstance(role.permissions, ServicePermissions)
    assert isinstance(role.permissions.user_reg, bool)
