from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from sqlmodel import select

from src.models.lead import Lead, LeadCreate
from src.services.user_services import login, register
from src.auth.security import ACCESS_TOKEN_EXPIRE_MINUTES


def test_login_success_returns_token():

    session = MagicMock()
    form_data = SimpleNamespace(username="testuser", password="password123")

    mock_user = MagicMock()
    mock_user.username = "testuser"

    with patch("src.services.user_services.authenticate_user") as mock_auth, \
            patch("src.services.user_services.create_access_token") as mock_token:
        mock_auth.return_value = mock_user
        mock_token.return_value = "fake-access-token"

        result = login(form_data, session)

    assert result.access_token == "fake-access-token"
    assert result.token_type == "bearer"
    mock_auth.assert_called_once_with("testuser", "password123", session)
    mock_token.assert_called_once()
    token_kwargs = mock_token.call_args.kwargs
    assert token_kwargs["data"] == {"sub": "testuser"}
    assert isinstance(token_kwargs["expires_delta"], timedelta)
    assert token_kwargs["expires_delta"].total_seconds(
    ) == ACCESS_TOKEN_EXPIRE_MINUTES * 60


# login
def test_login_returns_valid_token(mocker):

    session = MagicMock()

    form_data = MagicMock()
    form_data.username = "testuser"
    form_data.password = "testpassword"

    mock_auth = mocker.patch("src.services.user_services.authenticate_user")
    mock_auth.return_value = MagicMock(username="testuser")

    mock_token = mocker.patch("src.services.user_services.create_access_token")
    mock_token.return_value = "fake-access-token"

    result = login(form_data=form_data, session=session)

    assert result.access_token == mock_token.return_value
    assert result.token_type == "bearer"
    mock_auth.assert_called_once_with(
        form_data.username, form_data.password, session)
    mock_token.assert_called_once()
    token_kwargs = mock_token.call_args.kwargs
    assert token_kwargs["data"] == {"sub": "testuser"}
    assert isinstance(token_kwargs["expires_delta"], timedelta)
    assert token_kwargs["expires_delta"].total_seconds(
    ) == ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_login_failure_raises_http_exception(mocker):

    session = MagicMock()

    form_data = MagicMock()
    form_data.username = "invalid"
    form_data.password = "wrong"

    mock_auth = mocker.patch("src.services.user_services.authenticate_user")
    mock_auth.return_value = MagicMock(None)

    mock_token = mocker.patch("src.services.user_services.create_access_token")
    mock_token.side_effect = HTTPException(status_code=401)

    with pytest.raises(HTTPException):
        result = login(form_data, session)

        mock_auth.assert_called_once_with(
            form_data.username, form_data.password, session)
        mock_token.assert_called_once()
        assert result.status_code == 401
