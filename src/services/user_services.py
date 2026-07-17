from datetime import timedelta

from fastapi import HTTPException, status

from src.auth.security import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_user, fake_users_db
from src.schemas.user import Token


# Create a function called login that will receive the form_data from the function login_for_access_token at the path "/token" and return a Token object (which is an instance of the Token class)
def login(form_data):
    # Create a user object by calling the authenticate_user function from the security module passing the fake_users_db, form_data.username, and form_data.password as arguments. The authenticate_user function use the get user function to check if the user exists in the fake_users_db and if the password is correct.
    user = authenticate_user(
        fake_users_db, form_data.username, form_data.password)
    if not user:
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
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Return an instance on the Token class with the access_token attribute set to the newly created access token and the token_type set to "bearer"
    return Token(access_token=access_token, token_type="bearer")
