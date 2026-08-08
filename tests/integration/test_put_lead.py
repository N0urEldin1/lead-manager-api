from sqlmodel import select

from src.models.lead import Lead

from tests.conftest import create_leads


def test_put_lead_returns_200_and_persisting_the_lead(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.put(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    # Check the response status code and the returned data

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


def test_put_lead_unauthenticated_returns_401_without_persisting(testing_session, fake_unauthenticated_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.put(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_unauthenticated_user_headers,
    )

    assert response.status_code == 401

    # Check that the lead was not persisted in the database with the updated values (it should remain unchanged)

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_put_lead_inactive_returns_400_without_persisting(testing_session, fake_unauthenticated_inactive_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.put(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_unauthenticated_inactive_user_headers,
    )

    # Check that the lead was not persisted in the database with the updated values (it should remain unchanged)

    assert response.status_code == 400

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_put_lead_unauthorized_returns_404_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, second_fake_user, create_test_session):

    # Create a lead for the first user

    create_leads(create_test_session, fake_current_user, 1)

    # Create a lead for the second user

    other_lead = create_leads(create_test_session, second_fake_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    # Try to update the second user's lead with the first user's credentials

    response = testing_session.put(
        f"/leads/{other_lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 404

    # Check that the lead was not persisted in the database with the updated values (it should remain unchanged)

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == other_lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == other_lead.name
    assert stored_lead.company == other_lead.company
    assert stored_lead.email == other_lead.email
    assert stored_lead.status == other_lead.status
    assert stored_lead.owner_id == second_fake_user.user_id


def test_put_lead_not_found_returns_404_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    nonexistent_id = lead.lead_id + 1

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.put(
        f"/leads/{nonexistent_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 404

    # Check that the lead was not persisted in the database with the updated values (it should remain unchanged)

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_put_lead_invalid_id_returns_422_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    response = testing_session.put(
        "/leads/invalid_id",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 422

    # Check that the lead was not persisted in the database with the updated values (it should remain unchanged)

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_put_missing_data_returns_422_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    # Create a payload with missing required fields (missing "email")

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "status": "Contacted"
    }

    response = testing_session.put(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 422

    # Check that the response contains the expected error details

    assert response.json()["detail"]

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_put_invalid_data_returns_422_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    # Create a payload with invalid data (status should be a string, not an integer)

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": 123
    }

    response = testing_session.put(
        f"/leads/{lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 422

    # Check that the lead was not persisted in the database with the updated values (it should remain unchanged)

    stored_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()

    assert stored_lead is not None
    assert stored_lead.name == lead.name
    assert stored_lead.company == lead.company
    assert stored_lead.email == lead.email
    assert stored_lead.status == lead.status


def test_put_lead_updates_only_the_target_record(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    # Create two leads and assign lead 0 to target_lead and lead 1 to other_lead

    leads = create_leads(create_test_session, fake_current_user, 2)
    target_lead = leads[0]
    other_lead = leads[1]

    payload = {
        "name": "Updated Lead",
        "company": "Updated Company",
        "email": "updated@example.com",
        "status": "Contacted"
    }

    # Try to update the target lead using it's id

    response = testing_session.put(
        f"/leads/{target_lead.lead_id}",
        json=payload,
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 200

    # Make sure that the database still contains two leads (No overwriting happened)

    all_leads = create_test_session.exec(
        select(Lead).where(Lead.owner_id == fake_current_user.user_id)
    ).all()

    assert len(all_leads) == 2

    updated_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == target_lead.lead_id)
    ).first()
    unchanged_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == other_lead.lead_id)
    ).first()

    # Verify that the persisted data is correct

    assert updated_lead is not None
    assert updated_lead.name == payload["name"]
    assert updated_lead.company == payload["company"]
    assert updated_lead.email == payload["email"]
    assert updated_lead.status == payload["status"]

    # Verify that the other lead is unchanged

    assert unchanged_lead is not None
    assert unchanged_lead.name == other_lead.name
    assert unchanged_lead.company == other_lead.company
    assert unchanged_lead.email == other_lead.email
    assert unchanged_lead.status == other_lead.status
