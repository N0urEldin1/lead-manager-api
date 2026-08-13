from unittest.mock import MagicMock

from fastapi import HTTPException
import pytest

from src.models.lead import Lead
from src.services.lead_services import patch


# patch
def test_patch_applies_partial_updates_to_existing_lead():

    user = MagicMock()
    user.user_id = 1

    existing_lead = Lead(
        owner_id=1,
        name="old name",
        company="old company",
        email="old@email.com",
        status="old status"
    )

    lead = MagicMock()
    lead.model_dump.return_value = {
        "name": "new name",
        "status": "new status"
    }

    session = MagicMock()
    session.scalars.return_value.first.return_value = existing_lead

    result = patch(
        user=user,
        lead_id=1,
        lead=lead,
        session=session
    )

    assert result == {"data": existing_lead}
    assert existing_lead.name == "new name"
    assert existing_lead.status == "new status"
    assert existing_lead.company == "old company"
    assert existing_lead.email == "old@email.com"

    session.add.assert_called_once_with(existing_lead)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(existing_lead)


def test_patch_raises_404_when_lead_not_found():
    user = MagicMock()
    user.user_id = 1

    session = MagicMock()
    session.scalars.return_value.first.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        patch(
            user=user,
            lead_id=1,
            lead=MagicMock(),
            session=session
        )

    assert excinfo.value.status_code == 404

    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.refresh.assert_not_called()
