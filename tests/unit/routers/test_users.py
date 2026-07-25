from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from pytest_mock import mocker

from src.app import app

client = TestClient(app)


# GET /items
def test_get_items_unauthenticated_returns_401():

    response = client.get("/items/")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Unauthorized. Please login to access this resource"}


def test_get_items_returns_200(mocker, authenticated_user):

    mock_get = mocker.patch("src.routers.users.read_items")

    mock_get.return_value = "faketoken"

    header = {
        "Authorization": "Bearer faketoken",
        "Content-Type": "application/json"
    }

    response = authenticated_user.get("/items/", headers=header)

    assert response.status_code == 200
    assert response.json() == {"token": "faketoken"}


# POST /token
def test_post_token_returns_200(mocker):

    mock_post = mocker.patch("src.services.user_services.login")

    mock_post.return_value = {
        "access_token": "test_token", "token_type": "bearer"}

    response = client.post(
        "/token",
        data={
            "username": "Admin",
            "password": "123456789"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test_token", "token_type": "bearer"}
    # Check that the login function was called with the correct arguments
    # "http://127.0.0.1:8000/api/v1/token"
    mock_post.assert_called_once_with(mocker.ANY, mocker.ANY)


def test_post_token_unauthenticated_returns_401(mocker):

    mock_post = mocker.patch("src.services.user_services.login")

    mock_post.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized. Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    response = client.post(
        "/token",
        data={
            "username": "Admin",
            "password": "123456789"
        }
    )

    assert response.status_code == 401
    # assert response.json() == {
    #     "access_token": "test_token", "token_type": "bearer"}
    # Check that the login function was called with the correct arguments
    # "http://127.0.0.1:8000/api/v1/token"
    mock_post.assert_called_once_with(mocker.ANY, mocker.ANY)


def test_post_token_missing_password_returns_422(mocker):

    mock_post = mocker.patch("src.services.user_services.login")

    mock_post.return_value = {
        "access_token": "test_token", "token_type": "bearer"}

    response = client.post(
        "/token",
        data={
            "username": "Admin"
        }
    )

    assert response.status_code == 422


def test_post_token_missing_username_returns_422(mocker):

    mock_post = mocker.patch("src.services.user_services.login")

    mock_post.return_value = {
        "access_token": "test_token", "token_type": "bearer"}

    response = client.post(
        "/token",
        data={
            "password": "123456789"
        }
    )

    assert response.status_code == 422


# POST /register
def test_post_register_returns_201(mocker):

    mock_post = mocker.patch("src.services.user_services.register")

    mock_post.return_value = {
        "access_token": "test_token", "token_type": "bearer"}

    response = client.post(
        "/register",
        json={
            "username": "Admin",
            "email": "admin@email.com",
            "password": "123456789"
        }
    )
    assert response.status_code == 201
    assert response.json() == {
        "access_token": "test_token", "token_type": "bearer"}


def test_post_register_returns_400(mocker):

    mock_post = mocker.patch("src.services.user_services.register")

    mock_post.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already exists",
    )

    response = client.post(
        "/register",
        json={
            "username": "Admin",
            "email": "admin@email.com",
            "password": "123456789"
        }
    )

    assert response.status_code == 400


def test_post_register_missing_required_field_returns_422(mocker):

    mock_post = mocker.patch("src.services.user_services.register")

    mock_post.return_value = {
        "access_token": "test_token", "token_type": "bearer"}

    response = client.post(
        "/register",
        json={
            "email": "admin@email.com",
            "password": "123456789"
        }
    )
    assert response.status_code == 422


# GET /user/me
def test_get_user_returns_200(mocker, authenticated_user):

    mock_get = mocker.patch("src.routers.users.read_users_me")

    mock_get.return_value = {
        "email": None,
        "full_name": None,
        "disabled": None,
        "hashed_password": "fakehashedpassword",
        "username": "testuser",
        "user_id": 1,
        "is_superuser": None
    }

    header = {
        "Authorization": "Bearer faketoken",
        "Content-Type": "application/json"
    }

    response = authenticated_user.get("/users/me", headers=header)

    assert response.status_code == 200
    assert response.json() == {
        "email": None,
        "full_name": None,
        "disabled": False,
        "hashed_password": "fakehashedpassword",
        "username": "testuser",
        "user_id": 1,
        "is_superuser": False
    }


def test_get_user_no_token_returns_401():

    response = client.get("/items/")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Unauthorized. Please login to access this resource"}
