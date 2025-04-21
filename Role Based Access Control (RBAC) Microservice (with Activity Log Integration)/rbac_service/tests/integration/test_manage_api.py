# tests/integration/test_manage_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
# --- Updated Mocking Imports ---
from unittest.mock import patch, MagicMock # Keep patch and MagicMock
# Remove asyncio and AsyncMock if not needed elsewhere
# -----------------------------

# Import schemas if needed
from app.schemas.rbac import RoleResponse, PermissionResponse
# Import models to help verify database state
from app.models.rbac import Role, Permission

# client and db_session fixtures are automatically available from conftest.py

# --- Helper Functions ---
# (Keep your existing helper functions create_role_via_api and create_permission_via_api)
def create_role_via_api(client: TestClient, name: str, desc: str) -> dict:
    response = client.post("/api/v1/roles", json={"role_name": name, "description": desc})
    assert response.status_code == 201, f"Failed to create role: {response.text}"
    return response.json()

def create_permission_via_api(client: TestClient, name: str, desc: str, enabled: bool = True) -> dict:
    response = client.post("/api/v1/permissions", json={"permission_name": name, "description": desc, "is_enabled": enabled})
    assert response.status_code == 201, f"Failed to create permission: {response.text}"
    return response.json()

# --- Role API Integration Tests ---
# (Keep all your existing tests for Role CRUD: test_create_role_endpoint, test_create_role_duplicate_name, etc.)

def test_create_role_endpoint(client: TestClient, db_session: Session):
    role_data = {"role_name": "Integ Role Create", "description": "Created via API"}
    response = client.post("/api/v1/roles", json=role_data)
    assert response.status_code == 201
    data = response.json()
    assert data["role_name"] == role_data["role_name"]
    role_id = data["role_id"]
    db_role = db_session.get(Role, UUID(role_id))
    assert db_role is not None
    assert db_role.role_name == role_data["role_name"]

def test_create_role_duplicate_name(client: TestClient):
    """Test creating a role with a name that already exists."""
    create_role_via_api(client, "Duplicate Role Name", "")
    response = client.post("/api/v1/roles", json={"role_name": "Duplicate Role Name", "description": "Second attempt"})
    assert response.status_code == 409 # Conflict

def test_get_role_endpoint(client: TestClient, db_session: Session):
    role = create_role_via_api(client, "Role To Get Integ", "Fetch me")
    role_id = role["role_id"]
    response = client.get(f"/api/v1/roles/{role_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["role_id"] == role_id
    assert data["role_name"] == "Role To Get Integ"

def test_get_nonexistent_role_endpoint(client: TestClient):
    response = client.get(f"/api/v1/roles/{uuid4()}")
    assert response.status_code == 404

def test_update_role_endpoint(client: TestClient, db_session: Session):
    role = create_role_via_api(client, "Role To Update Integ", "Original Desc")
    role_id = role["role_id"]
    update_data = {"role_name": "Updated Role Name Integ", "description": "Updated Desc"}
    response = client.put(f"/api/v1/roles/{role_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["role_name"] == update_data["role_name"]
    assert data["description"] == update_data["description"]
    db_role = db_session.get(Role, UUID(role_id))
    assert db_role is not None
    assert db_role.role_name == update_data["role_name"]

def test_update_role_nonexistent(client: TestClient):
    """Test updating a role that doesn't exist."""
    update_data = {"role_name": "Update Nonexistent"}
    response = client.put(f"/api/v1/roles/{uuid4()}", json=update_data)
    assert response.status_code == 404

def test_update_role_conflicting_name(client: TestClient):
    """Test updating a role name to one that already exists."""
    role1 = create_role_via_api(client, "Conflict Role 1", "")
    role2 = create_role_via_api(client, "Conflict Role 2", "")
    role1_id = role1["role_id"]
    role2_name = role2["role_name"]
    update_data = {"role_name": role2_name}
    response = client.put(f"/api/v1/roles/{role1_id}", json=update_data)
    assert response.status_code == 409 # Conflict

def test_delete_role_endpoint(client: TestClient, db_session: Session):
    role = create_role_via_api(client, "Role To Delete Integ", "Delete me")
    role_id = role["role_id"]
    response = client.delete(f"/api/v1/roles/{role_id}")
    assert response.status_code == 204
    db_role = db_session.get(Role, UUID(role_id))
    assert db_role is None
    get_response = client.get(f"/api/v1/roles/{role_id}")
    assert get_response.status_code == 404

def test_delete_role_nonexistent(client: TestClient):
    """Test deleting a role that doesn't exist."""
    response = client.delete(f"/api/v1/roles/{uuid4()}")
    assert response.status_code == 404

# --- Permission API Integration Tests ---
# (Keep all your existing Permission CRUD tests) ...

def test_create_permission_endpoint(client: TestClient, db_session: Session):
    perm_data = {"permission_name": "perm:integ_create_v2", "description": "Created", "is_enabled": True}
    response = client.post("/api/v1/permissions", json=perm_data)
    assert response.status_code == 201
    data = response.json()
    assert data["permission_name"] == perm_data["permission_name"]
    db_perm = db_session.get(Permission, UUID(data["permission_id"]))
    assert db_perm is not None
    assert db_perm.permission_name == perm_data["permission_name"]

def test_create_permission_duplicate_name(client: TestClient):
    """Test creating a permission with a name that already exists."""
    create_permission_via_api(client, "duplicate:perm_name", "")
    response = client.post("/api/v1/permissions", json={"permission_name": "duplicate:perm_name", "description": ""})
    assert response.status_code == 409

def test_update_permission_endpoint(client: TestClient, db_session: Session):
    perm = create_permission_via_api(client, "perm:integ_update_v2", "Original Desc", True)
    perm_id = perm["permission_id"]
    update_data = {"description": "Updated Desc", "is_enabled": False}
    response = client.put(f"/api/v1/permissions/{perm_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["is_enabled"] is False
    db_perm = db_session.get(Permission, UUID(perm_id))
    assert db_perm is not None
    assert db_perm.is_enabled is False

def test_delete_permission_endpoint_unassigned(client: TestClient, db_session: Session):
    perm = create_permission_via_api(client, "perm:integ_delete_ok_v2", "Delete Me", True)
    perm_id = perm["permission_id"]
    response = client.delete(f"/api/v1/permissions/{perm_id}")
    assert response.status_code == 204
    db_perm = db_session.get(Permission, UUID(perm_id))
    assert db_perm is None


# --- Assignment API Integration Tests ---
# (Keep all your existing Assignment tests) ...

def test_assign_and_remove_permission_to_role(client: TestClient, db_session: Session):
    role = create_role_via_api(client, "Role Assign Test V2", "")
    perm = create_permission_via_api(client, "perm:assign_test_v2", "", True)
    role_id = role["role_id"]
    perm_id = perm["permission_id"]
    assign_response = client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": perm_id})
    assert assign_response.status_code == 200
    db_role = db_session.get(Role, UUID(role_id))
    assert len(db_role.permissions) == 1
    delete_perm_response = client.delete(f"/api/v1/permissions/{perm_id}")
    assert delete_perm_response.status_code == 400
    remove_response = client.delete(f"/api/v1/roles/{role_id}/permissions/{perm_id}")
    assert remove_response.status_code == 200
    db_session.refresh(db_role)
    assert len(db_role.permissions) == 0
    delete_perm_response_ok = client.delete(f"/api/v1/permissions/{perm_id}")
    assert delete_perm_response_ok.status_code == 204

def test_assign_disabled_permission_to_role(client: TestClient, db_session: Session):
    """Test assigning a disabled permission to a role fails."""
    role = create_role_via_api(client, "Assign Disabled Role", "")
    perm_disabled = create_permission_via_api(client, "perm:assign_disabled_test", "", False)
    role_id = role["role_id"]
    perm_id = perm_disabled["permission_id"]
    assign_response = client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": perm_id})
    assert assign_response.status_code == 400 # Bad Request

def test_assign_nonexistent_permission_to_role(client: TestClient):
    """Test assigning a non-existent permission to a role."""
    role = create_role_via_api(client, "Assign Nonexistent Perm Role", "")
    role_id = role["role_id"]
    assign_response = client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": str(uuid4())})
    assert assign_response.status_code == 404 # Not Found

def test_assign_role_to_user(client: TestClient, db_session: Session):
    role = create_role_via_api(client, "User Assign Role V2", "")
    role_id = role["role_id"]
    user_id = f"test-user-{uuid4()}"
    assign_response = client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id})
    assert assign_response.status_code == 204
    from app.models.rbac import user_roles_table
    from sqlalchemy import select, and_
    stmt = select(user_roles_table).where(user_roles_table.c.user_id == user_id)
    result = db_session.execute(stmt).first()
    assert result is not None
    assert result.role_id == UUID(role_id)
    remove_response = client.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert remove_response.status_code == 204
    result_after_delete = db_session.execute(stmt).first()
    assert result_after_delete is None


# --- Check API Integration Tests ---
# (Keep your existing Check test) ...

def test_check_api_endpoint(client: TestClient, db_session: Session):
    role = create_role_via_api(client, "Check Role V2", "")
    perm_enabled = create_permission_via_api(client, "perm:check_enabled_v2", "", True)
    perm_disabled = create_permission_via_api(client, "perm:check_disabled_v2", "", False)
    perm_unassigned = create_permission_via_api(client, "perm:check_unassigned_v2", "", True)
    role_id = role["role_id"]
    user_id = f"check-user-{uuid4()}"
    client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": perm_enabled["permission_id"]})
    client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": perm_disabled["permission_id"]})
    client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id})
    check_response_allowed = client.post("/api/v1/check", json={"user_id": user_id, "permission": perm_enabled["permission_name"]})
    assert check_response_allowed.status_code == 200
    assert check_response_allowed.json() == {"allowed": True, "reason": None}
    check_response_disabled = client.post("/api/v1/check", json={"user_id": user_id, "permission": perm_disabled["permission_name"]})
    assert check_response_disabled.status_code == 200
    assert check_response_disabled.json() == {"allowed": False, "reason": None}
    check_response_unassigned = client.post("/api/v1/check", json={"user_id": user_id, "permission": perm_unassigned["permission_name"]})
    assert check_response_unassigned.status_code == 200
    assert check_response_unassigned.json() == {"allowed": False, "reason": None}
    check_response_nouser = client.post("/api/v1/check", json={"user_id": "non-existent-user", "permission": perm_enabled["permission_name"]})
    assert check_response_nouser.status_code == 200
    assert check_response_nouser.json() == {"allowed": False, "reason": None}
    check_response_noperm = client.post("/api/v1/check", json={"user_id": user_id, "permission": "non:existent"})
    assert check_response_noperm.status_code == 200
    assert check_response_noperm.json() == {"allowed": False, "reason": None}


# --- CORRECTED Mocked Test for Logging ---

# Patch BackgroundTasks.add_task in the specific endpoints module where it's imported and used
@patch("app.api.v1.endpoints.manage.BackgroundTasks.add_task")
def test_create_role_logs_activity(mock_add_task: MagicMock, client: TestClient): # No async def needed
    """Test creating a role adds a background task to log activity."""
    # --- Arrange ---
    role_data = {"role_name": "Test Logging Role BGTask", "description": "Check background task"}

    # --- Act ---
    response = client.post("/api/v1/roles", json=role_data) # Call the synchronous endpoint

    # --- Assert ---
    assert response.status_code == 201
    role_id = response.json()["role_id"]

    # Check that background_tasks.add_task was called once
    mock_add_task.assert_called_once()

    # Check the arguments it was called with
    call_args, call_kwargs = mock_add_task.call_args
    expected_kwargs_subset = {
        "action": "CREATE_ROLE",
        "status": "success",
        "resource_type": "Role",
        "resource_id": role_id,
        "details": {"role_name": "Test Logging Role BGTask"}
        # userId defaults to SYSTEM
    }

    # Assert that the log_activity function itself was passed as the first positional arg
    from app.core.logging_client import log_activity as target_log_func
    assert call_args[0] == target_log_func

    # Check if actual keyword arguments contain all keys/values from expected subset
    assert expected_kwargs_subset.items() <= call_kwargs.items()

# TODO: Add more mocked tests for other actions (update role, delete role, assign role, etc.)
#       verifying background_tasks.add_task is called with the correct arguments.