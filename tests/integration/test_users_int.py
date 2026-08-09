from src.auth.security import create_access_token
from src.dependencies.auth import FormDep
from src.services.user_services import login
from src.models.user import User
from sqlmodel import select


def test_get_items_correct_token_returns_200(testing_session, fake_authenticated_active_user_headers):

    # user = fake_current_user

    # payload = {
    #     "username": user.username, "password": user.hashed_password}

    response = testing_session.get(
        "/items/",
        headers=fake_authenticated_active_user_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {"token": data["token"]}


def test_get_items_no_token_returns_401(testing_session):

    response = testing_session.get(
        "/items/",
        headers=None
    )

    assert response.status_code == 401

    data = response.json()

    assert data == {
        "detail": "Unauthorized. Please login to access this resource"}


def test_post_valid_user_returns_200(fake_current_user, testing_session):

    user = fake_current_user

    payload = {
        "username": user.username, "password": "123456789"}

    response = testing_session.post(
        "/token",
        data=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"


# POST /token
def test_post_invalid_password_returns_401(fake_current_user, testing_session):

    user = fake_current_user

    payload = {
        "username": user.username, "password": "wrongpassword"}

    print(user.username)

    response = testing_session.post(
        "/token",
        data=payload
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Unauthorized. Incorrect username or password"


def test_post_unknown_username_returns_401(fake_current_user, testing_session):

    user = fake_current_user

    payload = {
        "username": "unknown", "password": "123456789"}

    print(user.username)

    response = testing_session.post(
        "/token",
        data=payload
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Unauthorized. Incorrect username or password"


def test_post_missing_username_returns_422(fake_current_user, testing_session):

    user = fake_current_user

    payload = {"password": "123456789"}

    print(user.username)

    response = testing_session.post(
        "/token",
        data=payload
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] != None


def test_post_missing_password_returns_422(fake_current_user, testing_session):

    user = fake_current_user

    payload = {"username": user.username}

    print(user.username)

    response = testing_session.post(
        "/token",
        data=payload
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] != None
    # {"detail": [{"loc": ["string", 0], "msg": "string",
    #              "type": "string", "input": "string", "ctx": {}}]}


def test_post_invalid_data_returns_422(fake_current_user, testing_session):

    user = fake_current_user

    payload = {"123"}

    print(user.username)

    response = testing_session.post(
        "/token",
        content=payload
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] != None


# POST /register
def test_post_register_new_user_returns_201_and_persisting_the_user(testing_session, create_test_session):

    payload = {
        "username": "user999",
        "email": "email1",
        "full_name": "fullname1",
        "password": "123"
    }

    response = testing_session.post(
        "/register",
        json=payload
    )

    assert response.status_code == 201

    created_user = create_test_session.exec(
        select(User).where(User.username == payload["username"])
    ).first()

    assert created_user is not None
    assert created_user.username == payload["username"]
    assert created_user.full_name == payload["full_name"]
    assert created_user.email == payload["email"]


def test_post_register_new_user_return_correct_token(testing_session, create_test_session):

    payload = {
        "username": "user999",
        "email": "email1",
        "full_name": "fullname1",
        "password": "123"
    }

    response = testing_session.post(
        "/register",
        json=payload
    )

    data = response.json()

    form_data = FormDep(
        username=payload["username"], password=payload["password"])

    token = login(form_data, create_test_session)

    assert data["access_token"] == token.access_token


def test_post_register_new_user_hashing_the_password(testing_session, create_test_session):

    payload = {
        "username": "user999",
        "email": "email1",
        "full_name": "fullname1",
        "password": "123"
    }

    testing_session.post(
        "/register",
        json=payload
    )

    created_user = create_test_session.exec(
        select(User).where(User.username == payload["username"])).first()

    assert created_user is not None
    assert isinstance(created_user.hashed_password, str)


def test_post_register_existing_user_returns_400_without_persisting(testing_session, create_test_session):

    payload1 = {
        "username": "user1",
        "email": "email1",
        "full_name": "fullname1",
        "password": "123"
    }

    testing_session.post(
        "/register",
        json=payload1
    )

    payload2 = {
        "username": "user1",
        "email": "email2",
        "full_name": "fullname2",
        "password": "123456"
    }

    response = testing_session.post(
        "/register",
        json=payload2
    )

    assert response.status_code == 400  # Should be 401?

    data = response.json()

    assert data["detail"] != None

    created_user1 = create_test_session.exec(
        select(User).where(User.username == payload1["username"])
    ).first()

    assert created_user1 is not None
    assert created_user1.username == payload1["username"]
    assert created_user1.full_name == payload1["full_name"]
    assert created_user1.email == payload1["email"]

    created_user2 = create_test_session.exec(
        select(User).where(User.username == payload2["username"])
    ).first()

    assert created_user2.username == created_user1.username


def test_post_register_missing_required_field_returns_422_without_persisting(testing_session, create_test_session):

    payload = {
        "username": "user999"
    }

    response = testing_session.post(
        "/register",
        json=payload
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] != None

    created_user = create_test_session.exec(
        select(User).where(User.username == payload["username"])
    ).first()

    assert created_user is None


# GET /users/me/
def test_get_user_returns_200_and_correct_user(testing_session, fake_current_user):

    payload = {
        "username": fake_current_user.username,
        "password": "123456789"
    }

    login_response = testing_session.post(
        "/token",
        data=payload
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = testing_session.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == fake_current_user.username
    assert data["email"] == fake_current_user.email
    assert data["full_name"] == fake_current_user.full_name


def test_get_user_no_token_returns_401(testing_session):

    response = testing_session.get(
        "/users/me/",
        headers=None
    )

    assert response.status_code == 401

    data = response.json()

    assert data == {
        "detail": "Unauthorized. Please login to access this resource"
    }


def test_get_user_invalid_token_returns_401(testing_session, fake_unauthenticated_user_headers):

    response = testing_session.get(
        "/users/me/",
        headers=fake_unauthenticated_user_headers
    )

    assert response.status_code == 401

    data = response.json()

    assert data == {
        "detail": "Unauthorized. Incorrect username or password"
    }


def test_get_user_inactive_user_returns_400(testing_session, fake_unauthenticated_inactive_user_headers):

    response = testing_session.get(
        "/users/me/",
        headers=fake_unauthenticated_inactive_user_headers
    )

    assert response.status_code == 400

    data = response.json()

    assert data == {"detail": "Inactive user"}


def test_get_user_unknown_token_user_returns_401(testing_session):

    token = create_access_token(data={"sub": "unknownuser"})

    response = testing_session.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401

    data = response.json()

    assert data == {
        "detail": "Unauthorized. Incorrect username or password"
    }
