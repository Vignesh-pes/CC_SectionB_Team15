# tests/unit/test_security.py
import pytest
from unittest.mock import MagicMock, create_autospec
from uuid import uuid4
from sqlalchemy.orm import Session

# Import the function to test
from app.core.security import check_user_permission

# We need to mock the db.execute call which is central to this function
def test_check_permission_allowed():
    """Test permission check when user has the required permission via a role."""
    mock_db = create_autospec(Session)
    user_id = "user-allowed"
    permission_name = "sec:read"

    # Mock the final exists() query result
    mock_execute = MagicMock()
    mock_execute.scalar.return_value = True # Simulate the permission link exists
    mock_db.execute.return_value = mock_execute

    allowed = check_user_permission(db=mock_db, user_id=user_id, permission_name=permission_name)

    assert allowed is True
    # Check db.execute was called (for the final exists() query)
    # This assumes the internal subqueries don't trigger separate execute calls easily mockable here.
    assert mock_db.execute.call_count >= 1

def test_check_permission_not_assigned():
    """Test permission check when user doesn't have the permission assigned via roles."""
    mock_db = create_autospec(Session)
    user_id = "user-denied"
    permission_name = "sec:write"

    # Mock the final exists() query result
    mock_execute = MagicMock()
    mock_execute.scalar.return_value = False # Simulate the permission link does NOT exist
    mock_db.execute.return_value = mock_execute

    allowed = check_user_permission(db=mock_db, user_id=user_id, permission_name=permission_name)

    assert allowed is False
    assert mock_db.execute.call_count >= 1

def test_check_permission_nonexistent_permission_name():
    """Test permission check when the permission name itself doesn't exist or is disabled."""
    # This scenario is implicitly handled by the current logic,
    # as the subquery for permission_id will be empty or NULL,
    # causing the final exists() check to return False.
    mock_db = create_autospec(Session)
    user_id = "user-nonexistent-perm"
    permission_name = "sec:does_not_exist"

    # Mock the final exists() query result
    mock_execute = MagicMock()
    mock_execute.scalar.return_value = False # Simulate the permission link does NOT exist
    mock_db.execute.return_value = mock_execute

    allowed = check_user_permission(db=mock_db, user_id=user_id, permission_name=permission_name)

    assert allowed is False
    assert mock_db.execute.call_count >= 1

# Note: Precisely unit testing the 'is_enabled' flag filtering within the subquery
# without actually executing SQL or having very complex mocks is hard.
# We rely on the integration tests (`test_check_api_endpoint`) to verify
# that disabled permissions correctly result in 'allowed: false'.