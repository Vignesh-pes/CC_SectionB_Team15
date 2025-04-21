# rbac_service/app/core/security.py
from sqlalchemy.orm import Session
from sqlalchemy import select, exists, and_

# Import the specific tables needed for the check query
from app.models.rbac import user_roles_table, role_permissions_table, Permission

def check_user_permission(db: Session, *, user_id: str, permission_name: str) -> bool:
    """
    Checks if a user has a specific, *enabled* permission through their assigned roles.

    Args:
        db: The SQLAlchemy database session.
        user_id: The ID of the user to check.
        permission_name: The name of the permission required (e.g., 'profile:edit').

    Returns:
        True if the user has the permission, False otherwise.
    """

    # 1. Subquery to find the ID of the required *and enabled* permission
    permission_id_subquery = select(Permission.permission_id)\
        .where(
            and_( # <-- Use and_ for multiple conditions
                Permission.permission_name == permission_name,
                Permission.is_enabled == True # <-- ADDED check for is_enabled
            )
        )\
        .scalar_subquery() # Get the ID as a scalar value for comparison

    # Return False immediately if the permission doesn't exist or isn't enabled
    # This requires fetching the subquery result first, slightly less efficient than pure exists check
    # permission_id = db.execute(select(permission_id_subquery)).scalar_one_or_none()
    # if permission_id is None:
    #     return False
    # -- Alternative: Keep the exists check below, which handles non-existent permission ID implicitly --

    # 2. Subquery to find all role IDs assigned to the user
    user_role_ids_subquery = select(user_roles_table.c.role_id)\
        .where(user_roles_table.c.user_id == user_id)\
        .subquery() # Get the user's roles

    # 3. Main query: Check if any entry exists in role_permissions table linking
    #    one of the user's roles to the required, enabled permission.
    permission_exists_query = select(
        exists().where(
            and_(
                role_permissions_table.c.role_id.in_(select(user_role_ids_subquery.c.role_id)), # Role is one of the user's roles
                role_permissions_table.c.permission_id == permission_id_subquery # Permission matches the required one (which we filtered by enabled status)
            )
        )
    )

    # Execute the query
    has_permission = db.execute(permission_exists_query).scalar()

    return has_permission or False # Return True if exists, False otherwise