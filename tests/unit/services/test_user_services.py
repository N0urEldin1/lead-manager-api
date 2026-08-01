from datetime import timedelta
from types import SimpleNamespace
from unittest import result
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from sqlmodel import select

from src.models.user import UserRegister
from src.services.user_services import login, register
from src.auth.security import ACCESS_TOKEN_EXPIRE_MINUTES


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


# register
def test_register_returns_token_and_creates_user(mocker):

    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()

    user = UserRegister(
        username="newuser",
        email="newuser@example.com",
        full_name="New User",
        password="newpassword",
    )

    mock_get_user = mocker.patch("src.services.user_services.get_user_from_db")
    mock_get_user.return_value = None

    mock_hash = mocker.patch("src.services.user_services.get_password_hash")
    mock_hash.return_value = "hashed-password"

    mock_token = mocker.patch("src.services.user_services.create_access_token")
    mock_token.return_value = "fake-access-token"

    result = register(user, session)

    assert result.access_token == mock_token.return_value
    assert result.token_type == "bearer"

    mock_get_user.assert_called_once_with(user.username, session)
    mock_hash.assert_called_once_with(user.password)

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    mock_token.assert_called_once()

    token_kwargs = mock_token.call_args.kwargs
    assert token_kwargs["data"] == {"sub": "newuser"}
    assert isinstance(token_kwargs["expires_delta"], timedelta)
    assert token_kwargs["expires_delta"].total_seconds(
    ) == ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_register_existing_user_raises_http_exception(mocker):

    session = MagicMock()

    user = UserRegister(
        username="existinguser",
        email="existinguser@example.com",
        full_name="Existing User",
        password="secret",
    )

    mock_get_user = mocker.patch("src.services.user_services.get_user_from_db")
    mock_get_user.return_value = MagicMock()

    mock_hash = mocker.patch("src.services.user_services.get_password_hash")
    mock_token = mocker.patch("src.services.user_services.create_access_token")

    with pytest.raises(HTTPException):
        result = register(user, session)

        mock_get_user.assert_called_once_with(user.username, session)

        session.add.assert_not_called()
        session.commit.assert_not_called()
        session.refresh.assert_not_called()
        mock_hash.assert_not_called()
        mock_token.assert_not_called()

        assert result.status_code == 400
