# app/db/migrations/env.py
import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine # Moved import higher
from sqlalchemy import pool
from alembic import context

# Add project root to Python path to allow imports like app.core, app.models
# Adjust '..' based on where alembic command is run relative to project root
# Assuming alembic runs from project root (rbac_service/), this should be okay
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# --- Import Base, Models, and Settings ---
# Make sure Base is imported first
from app.db.base import Base
# Import your settings
from app.core.config import settings
# >>> CORRECTED: Explicitly import your models module <<<
# This ensures SQLAlchemy models inheriting from Base are registered
from app.models import rbac # Or wherever your models are defined

# ----------------------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # Use metadata from your imported Base

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use the DATABASE_URL from settings to create an engine
    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool) # Use NullPool for online migration

    # Associate a connection with the context
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # Run migrations within a transaction
        with context.begin_transaction():
            context.run_migrations()

    # >>> CORRECTED: Removed duplicated block <<<
    # The previous code had a duplicated 'with connectable.connect()...' block here


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()