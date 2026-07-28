from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from datetime import timedelta, datetime, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest
from src.auth.security import get_user_from_db, authenticate_user, create_access_token, get_current_user


from config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


# get_user_from_db()
def test_get_user_from_db_returns_user():

    user = MagicMock()
    user.username = "user1"

    session = MagicMock()
    session.exec.return_value.first.return_value = user

    result = get_user_from_db(user.username, session)

    assert result is user
    session.exec.assert_called_once()
    session.exec.return_value.first.assert_called_once()


def test_get_user_from_db_returns_none():

    user = MagicMock()
    user.username = "user1"

    session = MagicMock()
    session.exec.return_value.first.return_value = None

    result = get_user_from_db(user, session)

    assert result is None
    session.exec.assert_called_once()
    session.exec.return_value.first.assert_called_once()


# authenticate_user()
def test_authenticate_user_returns_user(mocker):
    session = MagicMock()

    user = MagicMock()
    user.username = "Ali"

    mock_get_user = mocker.patch("src.auth.security.get_user_from_db")
    mock_get_user.return_value = user

    mock_verify = mocker.patch("src.auth.security.verify_password")
    mock_verify.return_value = True

    result = authenticate_user("Ali", "password", session)

    assert result == user


def test_authenticate_user_does_not_exist_returns_false(mocker):

    session = MagicMock()

    mock_get_user = mocker.patch("src.auth.security.get_user_from_db")
    mock_get_user.return_value = None

    mock_verify = mocker.patch("src.auth.security.verify_password")
    mock_verify.return_value = True

    result = authenticate_user("Ali", "password", session)

    assert result is False
    mock_verify.assert_called_once()
    mock_get_user.assert_called_once()


def test_authenticate_user_wrong_password_returns_false(mocker):

    session = MagicMock()

    user = MagicMock()
    user.username = "Ali"
    user.hashed_password = "fakehashedpassword"

    mock_get_user = mocker.patch("src.auth.security.get_user_from_db")
    mock_get_user.return_value = user

    mock_verify = mocker.patch("src.auth.security.verify_password")
    mock_verify.return_value = False

    result = authenticate_user("Ali", "password", session)

    assert result is False
    mock_get_user.assert_called_once_with("Ali", session)
    mock_verify.assert_called_once_with("password", user.hashed_password)


# create_access_token()
def test_create_access_token_returns_string():

    data = {"sub": "username"}

    expires_delta = timedelta(30)

    token = create_access_token(data, expires_delta)

    assert isinstance(token, str)


def test_create_access_token_preserves_payload():

    data = {"sub": "username"}

    expires_delta = timedelta(30)

    token = create_access_token(data, expires_delta)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    expire = datetime.now(timezone.utc) + expires_delta

    result = expire.timestamp()

    assert payload["exp"] == int(result)
    assert payload["sub"] == "username"


def test_create_access_token_uses_default_expiration():

    data = {"sub": "username"}

    token = create_access_token(data, None)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    result = expire.timestamp()

    assert payload["exp"] == int(result)
    assert payload["sub"] == "username"


# get_current_user
@pytest.mark.asyncio
async def test_get_current_user_with_no_token():

    token = None

    user = MagicMock()
    user.username = "user1"

    session = MagicMock()
    session.exec.return_value.first.return_value = user

    with pytest.raises(HTTPException):
        result = await get_current_user(token, session)

        assert result.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token():

    token = MagicMock()
    token.return_value = "faketoken"

    user = MagicMock()
    user.username = "user1"

    session = MagicMock()
    session.exec.return_value.first.return_value = user

    with pytest.raises(HTTPException):
        result = await get_current_user(token, session)

        assert result.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_does_not_exist():

    token = MagicMock()
    token.return_value = "faketoken"

    user = MagicMock()
    user.username = None

    session = MagicMock()
    session.exec.return_value.first.return_value = user

    with pytest.raises(HTTPException):
        result = await get_current_user(token, session)

        assert result.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_returns_user(mocker):

    valid_token = create_access_token({"sub": "user1"})

    session = MagicMock()

    mock_db_user = mocker.patch(
        "src.auth.security.get_user_from_db")
    mock_db_user.return_value = {
        "email": None,
        "full_name": None,
        "disabled": None,
        "hashed_password": "fakehashedpassword",
        "username": "user1",
        "user_id": 1,
        "is_superuser": None
    }

    result = await get_current_user(valid_token, session)

    mock_db_user.assert_called_once_with("user1", session)

    assert result == {
        "email": None,
        "full_name": None,
        "disabled": None,
        "hashed_password": "fakehashedpassword",
        "username": "user1",
        "user_id": 1,
        "is_superuser": None
    }
