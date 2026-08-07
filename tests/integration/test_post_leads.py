from sqlmodel import select

from src.models.lead import Lead


def test_post_lead_returns_201_and_persisting_the_lead(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    payload = {
        "name": "New Lead",
        "company": "Acme",
        "email": "new@example.com",
        "status": "New"
    }

    response = testing_session.post(
        "/leads",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["company"] == payload["company"]
    assert data["email"] == payload["email"]
    assert data["status"] == payload["status"]

    created_lead = create_test_session.exec(
        select(Lead).where(Lead.owner_id == fake_current_user.user_id)
    ).first()

    assert created_lead is not None
    assert created_lead.name == payload["name"]
    assert created_lead.company == payload["company"]
    assert created_lead.email == payload["email"]
    assert created_lead.status == payload["status"]


def test_post_lead_unauthenticated_returns_401_without_persisting(testing_session, fake_unauthenticated_user_headers, create_test_session):

    payload = {
        "name": "New Lead",
        "company": "Acme",
        "email": "new@example.com",
        "status": "New"
    }

    response = testing_session.post(
        "/leads",
        json=payload,
        headers=fake_unauthenticated_user_headers,
    )

    assert response.status_code == 401
    assert create_test_session.exec(select(Lead)).all() == []


def test_post_lead_inactive_returns_400_without_persisting(testing_session, fake_unauthenticated_inactive_user_headers, create_test_session):

    payload = {
        "name": "New Lead",
        "company": "Acme",
        "email": "new@example.com",
        "status": "New"
    }

    response = testing_session.post(
        "/leads",
        json=payload,
        headers=fake_unauthenticated_inactive_user_headers,
    )

    assert response.status_code == 400
    assert create_test_session.exec(select(Lead)).all() == []


def test_post_lead_missing_data_returns_422_without_persisting(testing_session, fake_authenticated_active_user_headers, create_test_session):

    payload = {
        "name": "New Lead",
        "company": "Acme",
        "status": "New"
    }

    response = testing_session.post(
        "/leads",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"]
    assert create_test_session.exec(select(Lead)).all() == []


def test_post_lead_invalid_data_returns_422_without_persisting(testing_session, fake_authenticated_active_user_headers, create_test_session):
    payload = {
        "name": 5,
        "company": "Acme",
        "email": "new@example.com",
        "status": "New"
    }

    response = testing_session.post(
        "/leads",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 422
    assert create_test_session.exec(select(Lead)).all() == []
