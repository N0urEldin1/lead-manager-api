
from sqlmodel import select

from src.models.lead import Lead


# Test database isolation using transactions and rollbacks
def test_database_is_empty(test_session):
    assert test_session.exec(select(Lead)).all() == []


def test_get_leads_unauthenticated_returns_401_int(unauthenticated_client):

    response = unauthenticated_client.get("/leads")

    assert response.status_code == 401


def test_get_leads_authenticated_returns_200_int(authenticated_client, active_auth_headers):

    response = authenticated_client.get("/leads", headers=active_auth_headers)

    assert response.status_code == 200


def test_get_leads_authenticated_inactive_returns_400_int(authenticated_client_inactive, inactive_auth_headers):

    response = authenticated_client_inactive.get(
        "/leads", headers=inactive_auth_headers)

    assert response.status_code == 400


def test_get_leads_return_empty_list_int(authenticated_client, active_auth_headers):

    response = authenticated_client.get("/leads", headers=active_auth_headers)

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


def test_get_leads_return_one_lead(authenticated_client, active_auth_headers_with_data, fake_current_user_with_data):

    data = fake_current_user_with_data

    response = authenticated_client.get(
        "/leads", headers=active_auth_headers_with_data)

    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "name": "Test Lead 1",
                "company": "Test Company 1",
                "email": "test1@example.com",
                "status": "new",
                "lead_id": data.lead.lead_id
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "item_count": 1,
        },
        "next_page": None,
        "previous_page": None
    }
