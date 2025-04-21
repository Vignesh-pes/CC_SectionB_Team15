# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool # Use StaticPool for SQLite in-memory testing
from fastapi.testclient import TestClient
import os

from app.main import app # Import your FastAPI app
from app.db.base import Base # Import your Base model
from app.db.session import get_db # Import the original dependency
from app.core.config import settings # Import settings

# --- Start Database Setup ---

# Determine Database URL for testing
TEST_DATABASE_URL_FROM_ENV = os.getenv("TEST_DATABASE_URL")

if TEST_DATABASE_URL_FROM_ENV:
    # Use the provided PostgreSQL Test URL
    print(f"Using Test Database (PostgreSQL): {TEST_DATABASE_URL_FROM_ENV}")
    DATABASE_URL_FOR_TEST = TEST_DATABASE_URL_FROM_ENV
    # Create engine for test PostgreSQL database
    engine = create_engine(DATABASE_URL_FOR_TEST)
    # Create sessionmaker for test PostgreSQL database
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Fallback to SQLite in-memory database if TEST_DATABASE_URL is not set
    print("WARNING: TEST_DATABASE_URL not set. Falling back to SQLite in-memory database.")
    DATABASE_URL_FOR_TEST = "sqlite:///:memory:"
    # Create engine for SQLite in-memory database
    # connect_args needed for SQLite to allow multi-thread access in tests
    engine = create_engine(
        DATABASE_URL_FOR_TEST, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    # Create sessionmaker for SQLite database
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to manage database schema (runs once per session)
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Create tables before tests run
    Base.metadata.create_all(bind=engine)
    yield # Let tests run
    # Drop tables after tests finish (important for in-memory DB too)
    Base.metadata.drop_all(bind=engine)

# Fixture to provide a test database session per test function
@pytest.fixture(scope="function")
def db_session() -> Session:
    connection = engine.connect()
    # For SQLite in-memory, transactions might behave differently,
    # but this structure is generally good practice.
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback() # Rollback changes after each test
    connection.close()

# Fixture to override the get_db dependency
@pytest.fixture(scope="function")
def override_get_db(db_session: Session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass # db_session fixture handles closing/rollback
    app.dependency_overrides[get_db] = _override_get_db
    yield
    del app.dependency_overrides[get_db]

# Fixture to provide a TestClient instance
@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    with TestClient(app) as c:
        yield c

# --- End Database Setup ---