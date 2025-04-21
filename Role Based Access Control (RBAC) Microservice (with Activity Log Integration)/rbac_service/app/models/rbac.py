# app/models/rbac.py
import uuid
from datetime import datetime, UTC # <-- Import UTC
from sqlalchemy import (
    Column, String, ForeignKey, Table, DateTime, UniqueConstraint, Boolean
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

# Association Table for the Many-to-Many relationship between Roles and Permissions
role_permissions_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.permission_id", ondelete="CASCADE"), primary_key=True),
    # Use lambda for default callable
    Column("assigned_at", DateTime, default=lambda: datetime.now(UTC))
)

# Association Table for the Many-to-Many relationship between Users and Roles
user_roles_table = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True),
    # Use lambda for default callable
    Column("assigned_at", DateTime, default=lambda: datetime.now(UTC))
)

class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Use lambda for default/onupdate callables
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions_table,
        back_populates="roles",
        passive_deletes=True
    )

class Permission(Base):
    __tablename__ = "permissions"

    permission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Use lambda for default/onupdate callables
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions_table,
        back_populates="permissions",
        passive_deletes=True
    )