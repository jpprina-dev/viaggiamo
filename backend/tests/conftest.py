"""Shared pytest fixtures for all tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.models.base import Base


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings with SQLite in-memory database."""
    return Settings(
        PROJECT_NAME="Viaggiamo Test",
        SECRET_KEY="test-secret-key-for-testing-only",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/1",
        BACKEND_CORS_ORIGINS=["http://localhost:3000"],
        ENVIRONMENT="testing",
        DEBUG=True,
    )


@pytest.fixture
async def test_db_engine(test_settings: Settings):
    """Create test database engine."""
    engine = create_async_engine(
        test_settings.DATABASE_URL,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client for testing FastAPI endpoints."""
    from unittest.mock import AsyncMock, patch

    # Create mock for create_tables that does nothing
    mock_create_tables = AsyncMock(return_value=None)

    # Patch in main.py where it's imported and used
    with patch("app.main.create_tables", mock_create_tables):
        # Import the already-created app instance
        from app.main import app

        # Create transport for the app
        transport = ASGITransport(app=app)

        # Create client - routes are already registered, no need for lifespan
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
def mock_create_tables(monkeypatch):
    """Mock the create_tables function to avoid database initialization."""

    async def mock_fn():
        pass

    monkeypatch.setattr("app.core.database.create_tables", mock_fn)


@pytest.fixture(scope="session", autouse=True)
def initialize_password_hash():
    """
    Initialize password hash before running security tests.

    This fixture ensures pwdlib is properly initialized with a simple password
    before running tests, avoiding initialization issues with long test passwords.
    """
    from pwdlib import PasswordHash

    # Create a password hash instance and hash a simple password to trigger initialization
    password_hash = PasswordHash.recommended()
    try:
        # Use a simple, short password for initialization
        password_hash.hash("init")
    except Exception:
        # If initialization fails, tests will handle it
        pass

    yield
