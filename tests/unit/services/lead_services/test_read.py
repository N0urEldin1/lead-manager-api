from unittest.mock import MagicMock

from fastapi import HTTPException
import pytest

from src.services.lead_services import read


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

    with pytest.raises(HTTPException) as excinfo:
        read(
            user=user,
            session=session,
            lead_id=1
        )

    assert excinfo.value.status_code == 404
