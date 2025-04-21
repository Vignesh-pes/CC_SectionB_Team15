# tests/unit/test_crud.py
import pytest
from unittest.mock import MagicMock, create_autospec, ANY # Import ANY
from uuid import uuid4, UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, insert, exists # Import necessary SQL elements
from sqlalchemy.sql.selectable import Select
# Import schemas and models used by CRUD functions
from app.schemas.rbac import RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate
from app.models.rbac import Role, Permission, user_roles_table, role_permissions_table

# Import the CRUD module we are testing
from app.crud import rbac as crud

# --- Role CRUD Unit Tests ---

def test_create_role():
    mock_db = create_autospec(Session)
    role_in = RoleCreate(role_name="Unit Test Role", description="Desc")
    created_role = crud.create_role(db=mock_db, role_in=role_in)
    assert created_role.role_name == role_in.role_name
    assert created_role.description == role_in.description
    assert isinstance(created_role, Role)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(created_role)

def test_get_role():
    mock_db = create_autospec(Session)
    test_id = uuid4()
    expected_role = Role(role_id=test_id, role_name="Test Get Role")
    mock_db.get.return_value = expected_role
    fetched_role = crud.get_role(db=mock_db, role_id=test_id)
    assert fetched_role == expected_role
    mock_db.get.assert_called_once_with(Role, test_id)

def test_get_role_by_name():
    """Test getting a role by name unit."""
    mock_db = create_autospec(Session)
    role_name = "find_me_by_name"
    expected_role = Role(role_id=uuid4(), role_name=role_name)
    # Mock the execute().scalar_one_or_none() chain
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = expected_role
    mock_db.execute.return_value = mock_execute

    fetched_role = crud.get_role_by_name(db=mock_db, role_name=role_name)

    assert fetched_role == expected_role
    # Check that execute was called (can't easily check the exact statement without more complex mocking)
    mock_db.execute.assert_called_once()

def test_get_roles():
    """Test getting multiple roles unit."""
    mock_db = create_autospec(Session)
    expected_roles = [Role(role_id=uuid4(), role_name="Role 1"), Role(role_id=uuid4(), role_name="Role 2")]
    # Mock the execute().scalars().all() chain
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_roles
    mock_execute = MagicMock()
    mock_execute.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_execute

    fetched_roles = crud.get_roles(db=mock_db, skip=0, limit=10)

    assert fetched_roles == expected_roles
    mock_db.execute.assert_called_once() # Verify execute was called

def test_update_role():
    mock_db = create_autospec(Session)
    test_id = uuid4()
    existing_role = Role(role_id=test_id, role_name="Original Role")
    role_update_data = RoleUpdate(role_name="Updated Role Name", description="New Desc")
    updated_role = crud.update_role(db=mock_db, db_role=existing_role, role_in=role_update_data)
    assert updated_role.role_name == role_update_data.role_name
    assert updated_role.description == role_update_data.description
    assert updated_role == existing_role
    mock_db.add.assert_called_once_with(existing_role)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(existing_role)

def test_delete_role():
    mock_db = create_autospec(Session)
    test_id = uuid4()
    role_to_delete = Role(role_id=test_id, role_name="Delete Me")
    mock_db.get.return_value = role_to_delete
    result = crud.delete_role(db=mock_db, role_id=test_id)
    assert result is True
    mock_db.get.assert_called_once_with(Role, test_id)
    mock_db.delete.assert_called_once_with(role_to_delete)
    mock_db.commit.assert_called_once()

def test_delete_nonexistent_role():
    mock_db = create_autospec(Session)
    test_id = uuid4()
    mock_db.get.return_value = None
    result = crud.delete_role(db=mock_db, role_id=test_id)
    assert result is False
    mock_db.get.assert_called_once_with(Role, test_id)
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()

# --- Permission CRUD Unit Tests ---

def test_create_permission():
    mock_db = create_autospec(Session)
    perm_in = PermissionCreate(permission_name="unit:test", description="Test", is_enabled=True)
    created_perm = crud.create_permission(db=mock_db, permission_in=perm_in)
    assert created_perm.permission_name == perm_in.permission_name
    assert created_perm.is_enabled == perm_in.is_enabled
    assert isinstance(created_perm, Permission)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(created_perm)

def test_update_permission():
    mock_db = create_autospec(Session)
    test_id = uuid4()
    existing_perm = Permission(permission_id=test_id, permission_name="unit:update", is_enabled=True)
    perm_update_data = PermissionUpdate(description="New Desc", is_enabled=False)
    updated_perm = crud.update_permission(db=mock_db, db_permission=existing_perm, permission_in=perm_update_data)
    assert updated_perm.description == perm_update_data.description
    assert updated_perm.is_enabled == perm_update_data.is_enabled
    assert updated_perm == existing_perm
    mock_db.add.assert_called_once_with(existing_perm)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(existing_perm)

def test_delete_permission_not_assigned():
    mock_db = create_autospec(Session)
    test_id = uuid4()
    perm_to_delete = Permission(permission_id=test_id, permission_name="unit:delete_ok")
    mock_db.get.return_value = perm_to_delete
    mock_execute = MagicMock()
    mock_execute.scalar.return_value = False
    mock_db.execute.return_value = mock_execute
    result = crud.delete_permission(db=mock_db, permission_id=test_id)
    assert result is True
    mock_db.get.assert_called_once_with(Permission, test_id)
    assert mock_db.execute.call_count == 1
    mock_db.delete.assert_called_once_with(perm_to_delete)
    mock_db.commit.assert_called_once()

def test_delete_permission_assigned():
    mock_db = create_autospec(Session)
    test_id = uuid4()
    perm_to_delete = Permission(permission_id=test_id, permission_name="unit:delete_fail")
    mock_db.get.return_value = perm_to_delete
    mock_execute = MagicMock()
    mock_execute.scalar.return_value = True
    mock_db.execute.return_value = mock_execute
    result = crud.delete_permission(db=mock_db, permission_id=test_id)
    assert result is False
    mock_db.get.assert_called_once_with(Permission, test_id)
    assert mock_db.execute.call_count == 1
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()

# --- Assignment CRUD Unit Tests ---

def test_assign_permission_to_role():
    mock_db = create_autospec(Session)
    role = Role(role_id=uuid4(), role_name="RoleAssign", permissions=[])
    permission = Permission(permission_id=uuid4(), permission_name="perm:assign")
    updated_role = crud.assign_permission_to_role(db=mock_db, role=role, permission=permission)
    assert permission in updated_role.permissions
    assert updated_role == role
    mock_db.add.assert_called_once_with(role)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(role)

def test_assign_permission_to_role_already_assigned():
    mock_db = create_autospec(Session)
    permission = Permission(permission_id=uuid4(), permission_name="perm:assign")
    role = Role(role_id=uuid4(), role_name="RoleAssign", permissions=[permission])
    updated_role = crud.assign_permission_to_role(db=mock_db, role=role, permission=permission)
    assert permission in updated_role.permissions
    assert len(updated_role.permissions) == 1
    assert updated_role == role
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()

def test_remove_permission_from_role():
    """Test removing a permission from a role unit."""
    mock_db = create_autospec(Session)
    permission_to_remove = Permission(permission_id=uuid4(), permission_name="perm:remove_me")
    other_permission = Permission(permission_id=uuid4(), permission_name="perm:keep_me")
    role = Role(role_id=uuid4(), role_name="RoleRemove", permissions=[permission_to_remove, other_permission])

    updated_role = crud.remove_permission_from_role(db=mock_db, role=role, permission=permission_to_remove)

    assert permission_to_remove not in updated_role.permissions
    assert other_permission in updated_role.permissions
    assert len(updated_role.permissions) == 1
    assert updated_role == role
    mock_db.add.assert_called_once_with(role)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(role)

def test_remove_permission_from_role_not_assigned():
    """Test removing a permission that isn't assigned unit."""
    mock_db = create_autospec(Session)
    permission_not_assigned = Permission(permission_id=uuid4(), permission_name="perm:not_assigned")
    other_permission = Permission(permission_id=uuid4(), permission_name="perm:keep_me")
    role = Role(role_id=uuid4(), role_name="RoleRemove", permissions=[other_permission])

    updated_role = crud.remove_permission_from_role(db=mock_db, role=role, permission=permission_not_assigned)

    assert permission_not_assigned not in updated_role.permissions
    assert other_permission in updated_role.permissions
    assert len(updated_role.permissions) == 1
    assert updated_role == role
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()


def test_assign_role_to_user():
    """Test assigning a role to a user unit."""
    mock_db = create_autospec(Session)
    user_id = "test-user-assign"
    role_id = uuid4()

    mock_check_execute = MagicMock()
    mock_check_execute.first.return_value = None
    mock_insert_execute = MagicMock()

    # FIX: Use 'isinstance(stmt, Select)' instead of 'isinstance(stmt, select)'
    mock_db.execute.side_effect = lambda stmt: mock_check_execute if isinstance(stmt, Select) else mock_insert_execute

    crud.assign_role_to_user(db=mock_db, user_id=user_id, role_id=role_id)

    assert mock_db.execute.call_count == 2
    mock_db.commit.assert_called_once()

def test_assign_role_to_user_already_assigned():
    """Test assigning a role already assigned unit."""
    mock_db = create_autospec(Session)
    user_id = "test-user-assign"
    role_id = uuid4()

    # Mock the check for existing assignment (first() returns something)
    mock_check_execute = MagicMock()
    mock_check_execute.first.return_value = (user_id, role_id, None) # Simulate existing row
    mock_db.execute.return_value = mock_check_execute

    crud.assign_role_to_user(db=mock_db, user_id=user_id, role_id=role_id)

    # Check execute called once (only for select)
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_not_called() # No insert, so no commit needed

def test_remove_role_from_user():
    """Test removing a role from a user unit."""
    mock_db = create_autospec(Session)
    user_id = "test-user-remove"
    role_id = uuid4()

    crud.remove_role_from_user(db=mock_db, user_id=user_id, role_id=role_id)

    # Check execute called once (for delete)
    mock_db.execute.assert_called_once()
    # We can't easily assert the exact statement content without more complex mocking
    mock_db.commit.assert_called_once()

def test_get_user_roles():
    """Test getting roles for a user unit."""
    mock_db = create_autospec(Session)
    user_id = "test-user-get-roles"
    expected_roles = [Role(role_id=uuid4(), role_name="UserRole1")]
    # Mock the execute().scalars().all() chain
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_roles
    mock_execute = MagicMock()
    mock_execute.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_execute

    roles = crud.get_user_roles(db=mock_db, user_id=user_id)

    assert roles == expected_roles
    mock_db.execute.assert_called_once()