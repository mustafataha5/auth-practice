
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import (
    login_rate_limit,
    registration_rate_limit,
)
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.role import Role


# Use an isolated PostgreSQL database for testing.
TEST_DATABASE_URL = settings.database_url.set(
    database="auth_test_db"
)

if TEST_DATABASE_URL.database != "auth_test_db":
    raise RuntimeError("Unsafe test database configuration")


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Register all SQLAlchemy models, including RefreshTokenHistory.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=test_engine)

    yield

    # Drop tables only from the isolated test database.
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session(setup_database):
    with test_engine.connect() as connection:
        transaction = connection.begin()

        session = Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )

        try:
            session.add(Role(name="USER"))
            session.add(Role(name="ADMIN"))
            session.commit()

            yield session

        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    # Override database dependency.
    app.dependency_overrides[get_db] = override_get_db

    # Disable rate limiting in general tests.
    app.dependency_overrides[login_rate_limit] = lambda: None
    app.dependency_overrides[registration_rate_limit] = lambda: None

    try:
        with TestClient(app) as test_client:
            yield test_client

    finally:
        # Restore original dependencies after each test.
        app.dependency_overrides.clear()
