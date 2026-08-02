import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from src.app import app
from src.dependencies.auth import UserDep, get_current_active_user
from src.dependencies.database import get_session
from src.models.lead import Lead

from sqlmodel import SQLModel, Session, create_engine
from config import settings


@pytest.fixture
def fake_session():
    session = MagicMock()
    yield session
    session.close()


@pytest.fixture
def authenticated_user():

    def fake_session():
        session = MagicMock()
        yield session
        session.close()

    async def fake_current_user():
        return UserDep(
            user_id=1,
            username="testuser",
            email=None,
            full_name=None,
            disabled=False,
            is_superuser=False,
            hashed_password="fakehashedpassword"
        )

    app.dependency_overrides[get_current_active_user] = fake_current_user
    app.dependency_overrides[get_session] = fake_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def lead_create():
    def create(fake_session, **kwargs):
        lead = Lead(**kwargs)
        fake_session.add(lead)
        fake_session.commit()
        fake_session.refresh(lead)
        return lead
    return create


@pytest.fixture
def override_session():
    session = MagicMock()
    yield session
    session.close()

    app.dependency_overrides[get_session] = fake_session
    app.dependency_overrides.clear()


# Fixtures for integration tests


TEST_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture
def test_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def fake_current_user():
    return UserDep(
        user_id=1,
        username="testuser",
        email=None,
        full_name=None,
        disabled=False,
        is_superuser=False,
        hashed_password="fakehashedpassword"
    )


@pytest.fixture
def authenticated_client(test_session, fake_current_user):
    def override_get_session():
        yield test_session

    def override_get_current_user():
        return fake_current_user

    app.dependency_overrides[get_current_active_user] = override_get_current_user
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(test_session):
    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
