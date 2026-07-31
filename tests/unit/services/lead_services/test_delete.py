from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from sqlmodel import select

from src.models.lead import Lead, LeadCreate
from src.services.lead_services import read_all, read, create, delete, update


# delete
def test_delete_calls_delete_and_commit_when_found():

    user = MagicMock()
    user.user_id = 1

    lead = Lead(
        owner_id=1,
        name="name",
        company="company",
        email="email",
        status="status"
    )

    session = MagicMock()
    session.scalars.return_value.first.return_value = lead

    result = delete(
        user=user,
        lead_id=1,
        session=session
    )

    assert result is None
    session.delete.assert_called_once_with(lead)
    session.commit.assert_called_once()


def test_delete_raises_404_when_lead_not_found():

    user = MagicMock()
    user.user_id = 1

    session = MagicMock()
    session.scalars.return_value.first.return_value = None

    with pytest.raises(HTTPException):
        delete(
            user=user,
            lead_id=1,
            session=session
        )

    session.delete.assert_not_called()
    session.commit.assert_not_called()
