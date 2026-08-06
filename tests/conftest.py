import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from src.app import app
from src.auth.security import create_access_token
from src.dependencies.auth import UserDep, get_current_active_user
from src.dependencies.database import get_session
from src.models.lead import Lead

from sqlmodel import Session, StaticPool, create_engine
from config import settings

from dataclasses import dataclass


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

engine = create_engine(TEST_DATABASE_URL, poolclass=StaticPool)


@dataclass
class TestData:
    user: UserDep
    leads: list[Lead]


# Fixture to create an isolated session with transaction rollback for each test
@pytest.fixture
def create_test_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# Fixture to provide a TestClient with the overridden session for integration tests
@pytest.fixture
def testing_session(create_test_session):
    def override_get_session():
        yield create_test_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# Fixture to create a user and add it to the test session
@pytest.fixture
def fake_current_user(create_test_session):
    user = UserDep(
        user_id=1,
        username="testuser",
        email=None,
        full_name=None,
        disabled=False,
        is_superuser=False,
        hashed_password="fakehashedpassword"
    )

    create_test_session.add(user)
    create_test_session.commit()
    create_test_session.refresh(user)

    return user


# Fixtures to create authentication headers for different user states
@pytest.fixture
def fake_authenticated_active_user_headers(fake_current_user):

    user = fake_current_user

    token = create_access_token(
        data={"sub": str(user.username)}
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def fake_unauthenticated_inactive_user_headers(fake_current_user):

    user = fake_current_user
    user.disabled = True

    token = create_access_token(data={"sub": str(user.username)})

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def fake_unauthenticated_user_headers():
    return {"Authorization": f"Bearer invalidtoken"}


@pytest.fixture
def second_fake_user(create_test_session):
    user = UserDep(
        user_id=2,
        username="seconduser",
        email=None,
        full_name=None,
        disabled=False,
        is_superuser=False,
        hashed_password="fakehashedpassword"
    )

    create_test_session.add(user)
    create_test_session.commit()
    create_test_session.refresh(user)

    return user
