from sqlmodel import select

from src.models.lead import Lead

from tests.conftest import create_leads


def test_delete_lead_returns_204_and_persisting_deletion(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    leads = create_leads(create_test_session, fake_current_user, 2)

    target_lead = leads[0]

    response = testing_session.delete(
        f"/leads/{target_lead.lead_id}",
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 204

    deleted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == target_lead.lead_id)
    ).first()
    assert deleted_lead is None

    remaining_leads = create_test_session.exec(
        select(Lead).where(Lead.owner_id == fake_current_user.user_id)
    ).all()
    assert len(remaining_leads) == 1
    assert remaining_leads[0].lead_id == leads[1].lead_id


def test_delete_lead_unauthenticated_returns_401_without_persisting(testing_session, fake_unauthenticated_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    response = testing_session.delete(
        f"/leads/{lead.lead_id}",
        headers=fake_unauthenticated_user_headers,
    )

    assert response.status_code == 401

    persisted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()
    assert persisted_lead is not None
    assert persisted_lead.lead_id == lead.lead_id


def test_delete_lead_inactive_returns_400_without_persisting(testing_session, fake_unauthenticated_inactive_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    response = testing_session.delete(
        f"/leads/{lead.lead_id}",
        headers=fake_unauthenticated_inactive_user_headers,
    )

    assert response.status_code == 400

    persisted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()
    assert persisted_lead is not None
    assert persisted_lead.lead_id == lead.lead_id


def test_delete_lead_unauthorized_returns_404_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, second_fake_user, create_test_session):

    lead = create_leads(create_test_session, second_fake_user, 1)[0]

    response = testing_session.delete(
        f"/leads/{lead.lead_id}",
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 404

    persisted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()
    assert persisted_lead is not None
    assert persisted_lead.lead_id == lead.lead_id


def test_delete_lead_not_found_returns_404_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    response = testing_session.delete(
        f"/leads/{lead.lead_id + 1}",
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 404

    persisted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()
    assert persisted_lead is not None
    assert persisted_lead.lead_id == lead.lead_id


def test_delete_lead_invalid_id_returns_422_without_persisting(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    lead = create_leads(create_test_session, fake_current_user, 1)[0]

    response = testing_session.delete(
        "/leads/invalid_id",
        headers=fake_authenticated_active_user_headers,
    )

    assert response.status_code == 422

    persisted_lead = create_test_session.exec(
        select(Lead).where(Lead.lead_id == lead.lead_id)
    ).first()
    assert persisted_lead is not None
    assert persisted_lead.lead_id == lead.lead_id
