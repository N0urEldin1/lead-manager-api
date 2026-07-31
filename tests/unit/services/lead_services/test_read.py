from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from sqlmodel import select

from src.models.lead import Lead, LeadCreate
from src.services.lead_services import read_all, read, create, delete, update


# read
def test_read_returns_lead():

    user = MagicMock()
    user.user_id = 1

    data = {
        "name": "string",
                "company": "string",
                "email": "string",
                "status": "string",
                "lead_id": 1
    }

    session = MagicMock()
    session.scalars.return_value.first.return_value = data

    result = read(
        user=user,
        session=session,
        lead_id=1
    )

    assert result == {"data": data}


def test_read_returns_none_when_not_found():

    user = MagicMock()
    user.user_id = 1

    session = MagicMock()
    session.scalars.return_value.first.return_value = None

    with pytest.raises(HTTPException):
        result = read(
            user=user,
            session=session,
            lead_id=1
        )

        assert result.status_code == 404
