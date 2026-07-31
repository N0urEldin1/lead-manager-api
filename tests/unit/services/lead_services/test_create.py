from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from sqlmodel import select

from src.models.lead import Lead, LeadCreate
from src.services.lead_services import read_all, read, create, delete, update


# create
def test_create_creates_new_lead():

    user = MagicMock()
    user.user_id = 1

    lead = MagicMock()
    lead.name = "name"
    lead.email = "email"
    lead.company = "company"
    lead.status = "status"

    session = MagicMock()

    result = create(user, lead, session)

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    session.add.assert_called_once_with(result)
    session.refresh.assert_called_once_with(result)

    assert result.owner_id == user.user_id
    assert result.name == lead.name
    assert result.company == lead.company
    assert result.status == lead.status
    assert result.email == lead.email
