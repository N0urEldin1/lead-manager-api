import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from src.app import app
from src.dependencies.auth import UserDep, get_current_active_user
from src.dependencies.database import get_session
from src.models.lead import Lead


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
