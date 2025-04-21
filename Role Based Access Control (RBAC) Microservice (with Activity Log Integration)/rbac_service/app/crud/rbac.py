# rbac_service/app/crud/rbac.py
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, insert, text, exists, and_ # Added exists, and_
from typing import List, Optional, Dict, Any # Added Dict, Any
from uuid import UUID

# Import models, schemas, and association tables
from app.models.rbac import Role, Permission, user_roles_table, role_permissions_table # Import table
from app.schemas.rbac import RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate # Import Update Schemas

# --- Role CRUD ---

def get_role(db: Session, role_id: UUID) -> Optional[Role]:
    """Gets a single role by its ID."""
    return db.get(Role, role_id)

def get_role_by_name(db: Session, role_name: str) -> Optional[Role]:
    """Gets a single role by its name."""
    statement = select(Role).where(Role.role_name == role_name)
    return db.execute(statement).scalar_one_or_none()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """Gets a list of roles with pagination."""
    statement = select(Role).offset(skip).limit(limit).order_by(Role.role_name)
    return db.execute(statement).scalars().all()

def create_role(db: Session, *, role_in: RoleCreate) -> Role:
    """Creates a new role."""
    db_role = Role(**role_in.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, *, db_role: Role, role_in: RoleUpdate) -> Role:
    """Updates an existing role."""
    # Get role data as dict, excluding unset fields to support partial updates
    update_data = role_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    db.add(db_role) # Add to session to track changes
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, *, role_id: UUID) -> bool:
    """Deletes a role by its ID. Returns True if deleted, False otherwise."""
    db_role = db.get(Role, role_id)
    if db_role:
        # Cascading deletes in the DB should handle association tables
        db.delete(db_role)
        db.commit()
        return True
    return False

# --- Permission CRUD ---

def get_permission(db: Session, permission_id: UUID) -> Optional[Permission]:
    """Gets a single permission by its ID."""
    return db.get(Permission, permission_id)

def get_permission_by_name(db: Session, permission_name: str) -> Optional[Permission]:
     """Gets a single permission by its name."""
     statement = select(Permission).where(Permission.permission_name == permission_name)
     return db.execute(statement).scalar_one_or_none()

def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
    """Gets a list of permissions with pagination."""
    statement = select(Permission).offset(skip).limit(limit).order_by(Permission.permission_name)
    return db.execute(statement).scalars().all()

def create_permission(db: Session, *, permission_in: PermissionCreate) -> Permission:
    """Creates a new permission."""
    db_permission = Permission(**permission_in.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def update_permission(db: Session, *, db_permission: Permission, permission_in: PermissionUpdate) -> Permission:
    """Updates an existing permission."""
    update_data = permission_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_permission, field, value)
    db.add(db_permission) # Add to session to track changes
    db.commit()
    db.refresh(db_permission)
    return db_permission

def delete_permission(db: Session, *, permission_id: UUID) -> bool:
    """
    Deletes a permission by its ID ONLY if it's not assigned to any roles.
    Returns True if deleted, False otherwise (or if not found).
    """
    db_permission = db.get(Permission, permission_id)
    if not db_permission:
        return False # Not found

    # Check if the permission is assigned to any roles
    assignment_exists_stmt = select(exists().where(role_permissions_table.c.permission_id == permission_id))
    is_assigned = db.execute(assignment_exists_stmt).scalar()

    if is_assigned:
        # Optionally raise an exception or just return False
        # raise ValueError("Cannot delete permission: assigned to one or more roles.")
        return False # Indicate deletion failed due to assignment

    # If not assigned, proceed with deletion
    db.delete(db_permission)
    db.commit()
    return True


# --- Role-Permission Assignment CRUD ---

def assign_permission_to_role(db: Session, *, role: Role, permission: Permission) -> Role:
    """Assigns a permission to a role. Returns the updated Role."""
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role

def remove_permission_from_role(db: Session, *, role: Role, permission: Permission) -> Role:
    """Removes a permission from a role. Returns the updated Role."""
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role

# --- User-Role Assignment CRUD ---

def assign_role_to_user(db: Session, *, user_id: str, role_id: UUID) -> None:
    """Assigns a role to a user (inserts into user_roles table)."""
    check_stmt = select(user_roles_table).where(
        user_roles_table.c.user_id == user_id,
        user_roles_table.c.role_id == role_id
    )
    exists_result = db.execute(check_stmt).first()

    if not exists_result:
        insert_stmt = insert(user_roles_table).values(user_id=user_id, role_id=role_id)
        db.execute(insert_stmt)
        db.commit()

def remove_role_from_user(db: Session, *, user_id: str, role_id: UUID) -> None:
    """Removes a role from a user (deletes from user_roles table)."""
    delete_stmt = delete(user_roles_table).where(
         user_roles_table.c.user_id == user_id,
         user_roles_table.c.role_id == role_id
    )
    db.execute(delete_stmt)
    db.commit()

def get_user_roles(db: Session, *, user_id: str) -> List[Role]:
    """Gets all roles assigned to a specific user."""
    stmt = select(Role).join(user_roles_table).where(user_roles_table.c.user_id == user_id).order_by(Role.role_name)
    return db.execute(stmt).scalars().all()