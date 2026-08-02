
from sqlmodel import select

from src.models.lead import Lead


# Test database isolation using transactions and rollbacks
def test_database_is_empty(test_session):
    assert test_session.exec(select(Lead)).all() == []


def test_get_leads_unauthenticated_returns_401_int(unauthenticated_client):

    response = unauthenticated_client.get("/leads")

    assert response.status_code == 401


def test_get_leads_authenticated_returns_200_int(authenticated_client):

    response = authenticated_client.get("/leads")

    assert response.status_code == 200
