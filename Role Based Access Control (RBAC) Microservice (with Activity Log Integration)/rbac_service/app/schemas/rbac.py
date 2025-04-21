# app/schemas/rbac.py
from pydantic import (
    BaseModel, Field, ConfigDict, field_validator, model_validator # <-- Import model_validator
)
from uuid import UUID
from datetime import datetime
from typing import List, Optional

# --- Permission Schemas ---

class PermissionBase(BaseModel):
    permission_name: str = Field(..., min_length=3, max_length=100, description="Permission name (e.g., resource:action)")
    description: Optional[str] = Field(None, max_length=255, description="Detailed description of the permission")
    is_enabled: bool = Field(True, description="Whether the permission is active")

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    permission_name: Optional[str] = Field(None, min_length=3, max_length=100, description="New permission name")
    description: Optional[str] = Field(None, max_length=255, description="New detailed description")
    is_enabled: Optional[bool] = Field(None, description="Set permission active status")

class PermissionResponse(PermissionBase):
    permission_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Role Schemas ---

class RoleBase(BaseModel):
    role_name: str = Field(..., min_length=3, max_length=50, description="Name of the role")
    description: Optional[str] = Field(None, max_length=255, description="Detailed description of the role")

class RoleCreate(RoleBase):
   pass

class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, min_length=3, max_length=50, description="New name of the role")
    description: Optional[str] = Field(None, max_length=255, description="New detailed description")

class RoleResponse(RoleBase):
    role_id: UUID
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []
    model_config = ConfigDict(from_attributes=True)

# --- Assignment Schemas (for request bodies) ---

class RolePermissionAssignment(BaseModel):
    permission_id: Optional[UUID] = None
    permission_name: Optional[str] = None

    # Use Pydantic V2 model_validator for cross-field validation
    @model_validator(mode='after')
    def check_at_least_one_identifier(self) -> 'RolePermissionAssignment':
        if not self.permission_id and not self.permission_name:
            raise ValueError('Either permission_id or permission_name must be provided')
        return self

class UserRoleAssignment(BaseModel):
    role_id: Optional[UUID] = None
    role_name: Optional[str] = None

    # Use Pydantic V2 model_validator for cross-field validation
    @model_validator(mode='after')
    def check_at_least_one_identifier(self) -> 'UserRoleAssignment':
        if not self.role_id and not self.role_name:
            raise ValueError('Either role_id or role_name must be provided')
        return self
# --- Check Schemas ---

class CheckRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user performing the action")
    permission: str = Field(..., description="Permission name required (e.g., resource:action)")

class CheckResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None

# --- User Role Schemas ---
class UserRoleResponseItem(BaseModel):
    role_id: UUID
    role_name: str
    assigned_at: datetime
    model_config = ConfigDict(from_attributes=True)