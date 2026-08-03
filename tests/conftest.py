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
    lead: Lead


#
@pytest.fixture
def test_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# Authenticated active user fixture
@pytest.fixture
def fake_current_user(test_session):
    user = UserDep(
        user_id=1,
        username="testuser",
        email=None,
        full_name=None,
        disabled=False,
        is_superuser=False,
        hashed_password="fakehashedpassword"
    )

    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    return user


@pytest.fixture
def active_user_token(fake_current_user):
    return create_access_token(
        data={"sub": str(fake_current_user.username)}
    )


@pytest.fixture
def active_auth_headers(active_user_token):
    return {"Authorization": f"Bearer {active_user_token}"}


@pytest.fixture
def authenticated_client(test_session):
    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# Authenticated inactive user fixture
@pytest.fixture
def fake_current_user_inactive(test_session):
    user = UserDep(
        user_id=1,
        username="testuser",
        email=None,
        full_name=None,
        disabled=True,
        is_superuser=False,
        hashed_password="fakehashedpassword"
    )

    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    return user


@pytest.fixture
def inactive_user_token(fake_current_user_inactive):
    return create_access_token(
        data={"sub": str(fake_current_user_inactive.username)}
    )


@pytest.fixture
def inactive_auth_headers(inactive_user_token):
    return {"Authorization": f"Bearer {inactive_user_token}"}


@pytest.fixture
def authenticated_client_inactive(test_session):
    def override_get_session():
        yield test_session

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

    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# Fake user with data
@pytest.fixture
def fake_current_user_with_data(test_session):
    user = UserDep(
        user_id=1,
        username="testuser",
        email=None,
        full_name=None,
        disabled=False,
        is_superuser=False,
        hashed_password="fakehashedpassword"
    )

    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    lead1 = Lead(
        owner_id=user.user_id,
        name="Test Lead 1",
        company="Test Company 1",
        email="test1@example.com",
        status="new"
    )

    test_session.add(lead1)
    test_session.commit()
    test_session.refresh(lead1)

    return TestData(user=user, lead=lead1)


@pytest.fixture
def active_user_token_with_data(fake_current_user_with_data):

    data = fake_current_user_with_data

    return create_access_token(
        data={"sub": str(data.user.username)}
    )


@pytest.fixture
def active_auth_headers_with_data(active_user_token_with_data):
    return {"Authorization": f"Bearer {active_user_token_with_data}"}
