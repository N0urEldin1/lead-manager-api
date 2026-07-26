

from unittest.mock import MagicMock
from src.auth.security import get_user_from_db, authenticate_user


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
