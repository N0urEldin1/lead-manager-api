from sqlmodel import select

from src.models.lead import Lead

from tests.conftest import create_leads


def test_patch_lead_returns_200_and_persisting_the_lead(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.patch(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 200

    data = response.json()["data"]
    assert data["lead_id"] == lead.lead_id
    assert data["name"] == payload["name"]
    assert data["company"] == payload["company"]
    assert data["email"] == payload["email"]
    assert data["status"] == payload["status"]

    # Check that the lead was persisted in the database with the updated values

    persisted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert persisted_lead is not None
    assert persisted_lead.name == payload["name"]
    assert persisted_lead.company == payload["company"]
    assert persisted_lead.email == payload["email"]
    assert persisted_lead.status == payload["status"]
    assert persisted_lead.owner_id == fake_current_user.user_id


def test_patch_partial_update_only_updates_provided_fields(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Partially Updated Lead"
    }

    response = testing_session.patch(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 200

    # Check that only the name is updated

    data = response.json()["data"]
    assert data["lead_id"] == lead.lead_id
    assert data["name"] == payload["name"]
    assert data["company"] == lead.company
    assert data["email"] == lead.email
    assert data["status"] == lead.status

    persisted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    # Check that the updated data is persisted correctly

    assert persisted_lead is not None
    assert persisted_lead.name == payload["name"]
    assert persisted_lead.company == lead.company
    assert persisted_lead.email == lead.email
    assert persisted_lead.status == lead.status


def test_patch_no_fields_returns_200_without_changes(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    response = testing_session.patch(
        f"/leads/{lead.lead_id}",
        json={},
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 200

    data = response.json()["data"]
    assert data["lead_id"] == lead.lead_id
    assert data["name"] == lead.name
    assert data["company"] == lead.company
    assert data["email"] == lead.email
    assert data["status"] == lead.status

    persisted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert persisted_lead is not None
    assert persisted_lead.name == lead.name
    assert persisted_lead.company == lead.company
    assert persisted_lead.email == lead.email
    assert persisted_lead.status == lead.status


def test_patch_lead_unauthenticated_returns_401_without_persisting(testing_session, fake_unauthenticated_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.patch(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_unauthenticated_user_headers,
    )

    assert response.status_code == 401

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_patch_lead_inactive_returns_400_without_persisting(testing_session, fake_unauthenticated_inactive_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.patch(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_unauthenticated_inactive_user_headers,
    )

    assert response.status_code == 400

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_patch_lead_unauthorized_returns_404_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, second_fake_user, create_test_session):

    create_leads(create_test_session, fake_current_user, 1)

    other_lead = create_leads(create_test_session, second_fake_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.patch(
        f"/leads/{other_lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 404

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == other_lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == other_lead.name
    assert stored_lead.company == other_lead.company
    assert stored_lead.email == other_lead.email
    assert stored_lead.status == other_lead.status
    assert stored_lead.owner_id == second_fake_user.user_id


def test_patch_lead_not_found_returns_404_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    nonexistent_id = lead.lead_id + 1

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.patch(
        f"/leads/{nonexistent_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 404

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_patch_lead_invalid_id_returns_422_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.patch(
        "/leads/invalid_id",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 422

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_patch_invalid_data_returns_422_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": 123,
    }

    response = testing_session.patch(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 422

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status
