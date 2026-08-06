
from sqlmodel import select

from src.models.lead import Lead


# Test database isolation using transactions and rollbacks
def test_database_is_empty(create_test_session):
    assert create_test_session.exec(select(Lead)).all() == []


def test_get_leads_unauthenticated_returns_401_int(testing_session, fake_unauthenticated_user_headers):

    response = testing_session.get(
        "/leads", headers=fake_unauthenticated_user_headers)

    assert response.status_code == 401


def test_get_leads_authenticated_returns_200_int(testing_session, fake_authenticated_active_user_headers):

    response = testing_session.get(
        "/leads", headers=fake_authenticated_active_user_headers)

    assert response.status_code == 200


def test_get_leads_authenticated_inactive_returns_400_int(testing_session, fake_unauthenticated_inactive_user_headers):

    response = testing_session.get(
        "/leads", headers=fake_unauthenticated_inactive_user_headers)

    assert response.status_code == 400


def test_get_leads_return_empty_list_int(testing_session, fake_authenticated_active_user_headers):

    response = testing_session.get(
        "/leads", headers=fake_authenticated_active_user_headers)

    assert response.status_code == 200
    assert response.json() == {
        "data": [],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "item_count": 0,
        },
        "next_page": None,
        "previous_page": None
    }


def create_leads(session, user, count):

    leads = []
    for i in range(count):
        lead = Lead(
            owner_id=user.user_id,
            name=f"Test Lead {i + 1}",
            company=f"Test Company {i + 1}",
            email=f"test{i + 1}@example.com",
            status=f"New lead {i + 1}"
        )

        session.add(lead)

        leads.append(lead)

    session.flush()
    return leads


def test_get_leads_return_five_leads(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    count = 5

    user = fake_current_user

    create_leads(create_test_session, user, count)

    response = testing_session.get(
        "/leads", headers=fake_authenticated_active_user_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["data"][0]["name"] == "Test Lead 1"
    assert data["pagination"]["item_count"] == count
    assert len(data["data"]) == count


def test_get_leads_return_only_current_user_leads(testing_session, fake_authenticated_active_user_headers, fake_current_user, second_fake_user, create_test_session):

    # User 1 setup

    count1 = 2

    user1 = fake_current_user

    create_leads(create_test_session, user1, count1)

    # User 2 setup

    count2 = 2

    user2 = second_fake_user

    create_leads(create_test_session, user2, count2)

    response = testing_session.get(
        "/leads", headers=fake_authenticated_active_user_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["data"][0]["name"] == "Test Lead 1"
    assert data["data"][1]["name"] == "Test Lead 2"

    assert data["data"][0]["name"] != "Test Lead 3"

    assert data["pagination"]["item_count"] == count1
    assert len(data["data"]) == count1


def test_get_single_lead_unauthorized_returns_404_int(testing_session, fake_authenticated_active_user_headers, fake_current_user, second_fake_user, create_test_session):

    # User 1 setup

    count1 = 1

    user1 = fake_current_user

    leads_user1 = create_leads(create_test_session, user1, count1)

    # User 2 setup

    count2 = 1

    user2 = second_fake_user

    leads_user2 = create_leads(create_test_session, user2, count2)

    response = testing_session.get(
        f"/leads/{leads_user2[0].lead_id}", headers=fake_authenticated_active_user_headers)

    assert response.status_code == 404
