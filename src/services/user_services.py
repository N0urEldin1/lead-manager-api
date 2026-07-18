from datetime import timedelta
from sqlalchemy import select

from fastapi import HTTPException, status

from src.auth.security import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_password_hash, get_user_from_db
from src.models.user import User
from src.schemas.user import Token


# Create a function called login that will receive the form_data from the function login_for_access_token at the path "/token" and return a Token object (which is an instance of the Token class)
def login(form_data, session):
    # Create a user object by calling the authenticate_user function from the security module passing the fake_users_db, form_data.username, and form_data.password as arguments. The authenticate_user function use the get user function to check if the user exists in the fake_users_db and if the password is correct.

    # user = authenticate_user(
    #     fake_users_db, form_data.username, form_data.password)

    auth_user = authenticate_user(
        form_data.username, form_data.password, session)

    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # If a user exist in the database:
    # Create the access_token_expires object that's an instance of the timedelta class with minutes attribute set to the ACCESS_TOKEN_EXPIRE_MINUTES constant
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Create the access_token object by passing the user data as a dictionary with "sub" as the key and the username as the value to create_access_token's attribute "data" and the access_token_expires object to the expires_delta attribute
    access_token = create_access_token(
        data={"sub": auth_user.username}, expires_delta=access_token_expires
    )
    # Return an instance on the Token class with the access_token attribute set to the newly created access token and the token_type set to "bearer"
    return Token(access_token=access_token, token_type="bearer")


def register(user, session):  # form_data,
    # Check if the user already exists in the database by calling the get_user function from the security module passing the fake_users_db and form_data.username as arguments. The get_user function will return a user object if the user exists in the database or None if it doesn't.

    # From fake_users_db
    # existing_user = get_user(fake_users_db, user.username)

    existing_user = get_user_from_db(user.username, session)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    # If the user doesn't exist in the database, create a new user object by adding the new user's data to the fake_users_db dictionary with the username as the key and a dictionary with the user's data as the value. The password will be hashed using the get_password_hash function from the security module.
    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Return an instance of the Token class with the access_token attribute set to a newly created access token and the token_type set to "bearer"
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
