
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


def test_get_leads_return_five_leads(testing_session, active_auth_headers_with_data, fake_current_user_with_data):

    page_size = 5

    data = fake_current_user_with_data

    response = testing_session.get(
        f"/leads?page_size={page_size}", headers=active_auth_headers_with_data)

    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["item_count"] == page_size
    assert len(data["data"]) == page_size


def test_get_leads_return_ten_leads(testing_session, active_auth_headers_with_data, fake_current_user_with_data):

    page_size = 10

    data = fake_current_user_with_data

    response = testing_session.get(
        f"/leads?page_size={page_size}", headers=active_auth_headers_with_data)

    assert response.status_code == 200

    data = response.json()
    assert data["pagination"]["item_count"] == page_size
    assert len(data["data"]) == page_size
