# app/api/v1/endpoints/manage.py
# Corrected version using BackgroundTasks

# Add BackgroundTasks to imports, ensure asyncio is NOT imported directly here
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.schemas.rbac import (
    RoleCreate, RoleResponse, RoleUpdate,
    PermissionCreate, PermissionResponse, PermissionUpdate,
    RolePermissionAssignment,
    UserRoleAssignment,
    UserRoleResponseItem
)
from app.crud import rbac as crud
from app.models.rbac import Role, Permission
# Import the logging helper function and constants (log_activity is still async)
from app.core.logging_client import (
    log_activity,
    ACTION_CREATE_ROLE, ACTION_UPDATE_ROLE, ACTION_DELETE_ROLE,
    ACTION_CREATE_PERMISSION, ACTION_UPDATE_PERMISSION, ACTION_DELETE_PERMISSION,
    ACTION_ASSIGN_PERMISSION_TO_ROLE, ACTION_REMOVE_PERMISSION_FROM_ROLE,
    ACTION_ASSIGN_ROLE_TO_USER, ACTION_REMOVE_ROLE_FROM_USER
)

router = APIRouter()

# === Role Endpoints ===

@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Role",
    description="Create a new role."
)
def create_new_role( # Using def
    *,
    db: Session = Depends(get_db),
    role_in: RoleCreate,
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> RoleResponse:
    existing_role = crud.get_role_by_name(db=db, role_name=role_in.role_name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role with name '{role_in.role_name}' already exists.",
        )
    created_role = crud.create_role(db=db, role_in=role_in)

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_CREATE_ROLE,
        status="success",
        resource_type="Role",
        resource_id=str(created_role.role_id),
        details={"role_name": created_role.role_name}
        # user_id defaults to SYSTEM in log_activity
    )
    # ----------------------------------------
    return created_role

@router.get(
    "/roles",
    response_model=List[RoleResponse],
    summary="List Roles",
    description="Get a list of all roles with pagination."
)
def list_all_roles(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records")
) -> List[RoleResponse]:
    roles = crud.get_roles(db=db, skip=skip, limit=limit)
    return roles

@router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Get Role by ID",
    description="Get details for a specific role by its ID."
)
def get_role_by_id_endpoint(
    *,
    db: Session = Depends(get_db),
    role_id: UUID = Path(..., description="The ID of the role to retrieve")
) -> RoleResponse:
    role = crud.get_role(db=db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role

@router.put(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Update Role",
    description="Update details for a specific role by its ID."
)
def update_existing_role( # Using def
    *,
    db: Session = Depends(get_db),
    role_id: UUID = Path(..., description="The ID of the role to update"),
    role_in: RoleUpdate = Body(...),
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> RoleResponse:
    db_role = crud.get_role(db=db, role_id=role_id)
    if not db_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role_in.role_name and role_in.role_name != db_role.role_name:
        existing_role = crud.get_role_by_name(db=db, role_name=role_in.role_name)
        if existing_role and existing_role.role_id != role_id:
             raise HTTPException(
                 status_code=status.HTTP_409_CONFLICT,
                 detail=f"Role with name '{role_in.role_name}' already exists.",
             )

    updated_role = crud.update_role(db=db, db_role=db_role, role_in=role_in)

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_UPDATE_ROLE,
        status="success",
        resource_type="Role",
        resource_id=str(updated_role.role_id),
        details={"updated_fields": role_in.model_dump(exclude_unset=True)}
    )
    # ----------------------------------------
    return updated_role

@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Role",
    description="Delete a specific role by its ID."
)
def delete_existing_role( # Using def
    *,
    db: Session = Depends(get_db),
    role_id: UUID = Path(..., description="The ID of the role to delete"),
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> None:
    deleted = crud.delete_role(db=db, role_id=role_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_DELETE_ROLE,
        status="success",
        resource_type="Role",
        resource_id=str(role_id)
    )
    # ----------------------------------------
    return None

# === Permission Endpoints ===

@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Permission",
    description="Create a new permission."
)
def create_new_permission( # Using def
    *,
    db: Session = Depends(get_db),
    permission_in: PermissionCreate,
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> PermissionResponse:
    existing_perm = crud.get_permission_by_name(db=db, permission_name=permission_in.permission_name)
    if existing_perm:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Permission with name '{permission_in.permission_name}' already exists.",
        )
    created_perm = crud.create_permission(db=db, permission_in=permission_in)

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_CREATE_PERMISSION,
        status="success",
        resource_type="Permission",
        resource_id=str(created_perm.permission_id),
        details={"permission_name": created_perm.permission_name, "is_enabled": created_perm.is_enabled}
    )
    # ----------------------------------------
    return created_perm

@router.get(
    "/permissions",
    response_model=List[PermissionResponse],
    summary="List Permissions",
    description="Get a list of all permissions with pagination."
)
def list_all_permissions(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records")
) -> List[PermissionResponse]:
    permissions = crud.get_permissions(db=db, skip=skip, limit=limit)
    return permissions

@router.get(
    "/permissions/{permission_id}",
    response_model=PermissionResponse,
    summary="Get Permission by ID",
    description="Get details for a specific permission by its ID."
)
def get_permission_by_id_endpoint(
    *,
    db: Session = Depends(get_db),
    permission_id: UUID = Path(..., description="The ID of the permission to retrieve")
) -> PermissionResponse:
    permission = crud.get_permission(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return permission

@router.put(
    "/permissions/{permission_id}",
    response_model=PermissionResponse,
    summary="Update Permission",
    description="Update details for a specific permission by its ID."
)
def update_existing_permission( # Using def
    *,
    db: Session = Depends(get_db),
    permission_id: UUID = Path(..., description="The ID of the permission to update"),
    permission_in: PermissionUpdate = Body(...),
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> PermissionResponse:
    db_permission = crud.get_permission(db=db, permission_id=permission_id)
    if not db_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    if permission_in.permission_name and permission_in.permission_name != db_permission.permission_name:
         existing_perm = crud.get_permission_by_name(db=db, permission_name=permission_in.permission_name)
         if existing_perm and existing_perm.permission_id != permission_id:
             raise HTTPException(
                 status_code=status.HTTP_409_CONFLICT,
                 detail=f"Permission with name '{permission_in.permission_name}' already exists.",
             )

    updated_permission = crud.update_permission(db=db, db_permission=db_permission, permission_in=permission_in)

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_UPDATE_PERMISSION,
        status="success",
        resource_type="Permission",
        resource_id=str(updated_permission.permission_id),
        details={"updated_fields": permission_in.model_dump(exclude_unset=True)}
    )
    # ----------------------------------------
    return updated_permission

@router.delete(
    "/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Permission",
    description="Delete a specific permission by its ID. Fails if the permission is assigned to any role."
)
def delete_existing_permission( # Using def
    *,
    db: Session = Depends(get_db),
    permission_id: UUID = Path(..., description="The ID of the permission to delete"),
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> None:
    deleted = crud.delete_permission(db=db, permission_id=permission_id)
    if not deleted:
        db_permission = crud.get_permission(db=db, permission_id=permission_id)
        if not db_permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        else:
             # Log failure
             background_tasks.add_task(log_activity, action=ACTION_DELETE_PERMISSION, status="failure", resource_id=str(permission_id), details={"reason": "Permission Assigned"})
             raise HTTPException(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 detail="Cannot delete permission: it is currently assigned to one or more roles."
             )

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_DELETE_PERMISSION,
        status="success",
        resource_type="Permission",
        resource_id=str(permission_id)
    )
    # ----------------------------------------
    return None

# === Role <-> Permission Assignment Endpoints ===

@router.post(
    "/roles/{role_id}/permissions",
    response_model=RoleResponse,
    summary="Assign Permission to Role",
    description="Assign an existing, enabled permission to an existing role."
)
def assign_permission_to_role_endpoint( # Using def
    *,
    db: Session = Depends(get_db),
    role_id: UUID = Path(..., description="ID of the role"),
    assignment_in: RolePermissionAssignment,
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> RoleResponse:
    role = crud.get_role(db=db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found") # Corrected

    permission = None
    detail_404 = "Permission not found." # Corrected
    if assignment_in.permission_id:
        permission = crud.get_permission(db=db, permission_id=assignment_in.permission_id)
    elif assignment_in.permission_name:
        permission = crud.get_permission_by_name(db=db, permission_name=assignment_in.permission_name)

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_404) # Corrected

    if not permission.is_enabled:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign a disabled permission.") # Corrected

    updated_role = crud.assign_permission_to_role(db=db, role=role, permission=permission)

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_ASSIGN_PERMISSION_TO_ROLE,
        status="success",
        resource_type="RolePermissionAssignment",
        resource_id=str(role_id),
        details={"permission_id": str(permission.permission_id), "permission_name": permission.permission_name}
    )
    # ----------------------------------------
    return updated_role

@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=RoleResponse,
    summary="Remove Permission from Role",
    description="Remove a permission assignment from a role."
)
def remove_permission_from_role_endpoint( # Using def
    *,
    db: Session = Depends(get_db),
    role_id: UUID = Path(..., description="ID of the role"),
    permission_id: UUID = Path(..., description="ID of the permission to remove"),
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> RoleResponse:
    role = crud.get_role(db=db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    permission = crud.get_permission(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    updated_role = crud.remove_permission_from_role(db=db, role=role, permission=permission)

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_REMOVE_PERMISSION_FROM_ROLE,
        status="success",
        resource_type="RolePermissionAssignment",
        resource_id=str(role_id),
        details={"permission_id": str(permission.permission_id)}
    )
    # ----------------------------------------
    return updated_role

# === User <-> Role Assignment Endpoints ===

@router.post(
    "/users/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign Role to User",
    description="Assign an existing role to a user (by user ID)."
)
def assign_role_to_user_endpoint( # Using def
    *,
    db: Session = Depends(get_db),
    user_id: str = Path(..., description="ID of the user"),
    assignment_in: UserRoleAssignment,
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> None:
    role = None
    if assignment_in.role_id:
        role = crud.get_role(db=db, role_id=assignment_in.role_id)
    elif assignment_in.role_name:
        role = crud.get_role_by_name(db=db, role_name=assignment_in.role_name)

    if not role:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    crud.assign_role_to_user(db=db, user_id=user_id, role_id=role.role_id)

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_ASSIGN_ROLE_TO_USER,
        user_id=user_id, # The user being affected
        status="success",
        resource_type="UserRoleAssignment",
        resource_id=str(role.role_id),
        details={"assigned_role_name": role.role_name}
    )
    # ----------------------------------------
    return None

@router.delete(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Role from User",
    description="Remove a role assignment from a user."
)
def remove_role_from_user_endpoint( # Using def
    *,
    db: Session = Depends(get_db),
    user_id: str = Path(..., description="ID of the user"),
    role_id: UUID = Path(..., description="ID of the role to remove"),
    background_tasks: BackgroundTasks # Add BackgroundTasks dependency
) -> None:
    role = crud.get_role(db=db, role_id=role_id)
    if not role:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    crud.remove_role_from_user(db=db, user_id=user_id, role_id=role_id)

    # --- Log Success using BackgroundTasks ---
    background_tasks.add_task( # Use add_task
        log_activity,
        action=ACTION_REMOVE_ROLE_FROM_USER,
        user_id=user_id, # The user being affected
        status="success",
        resource_type="UserRoleAssignment",
        resource_id=str(role_id)
    )
    # ----------------------------------------
    return None

@router.get(
    "/users/{user_id}/roles",
    response_model=List[RoleResponse],
    summary="List User's Roles",
    description="Get a list of all roles assigned to a specific user."
)
def list_user_roles_endpoint(
    *,
    db: Session = Depends(get_db),
    user_id: str = Path(...)
) -> List[RoleResponse]:
    roles = crud.get_user_roles(db=db, user_id=user_id)
    return roles