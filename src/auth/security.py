from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlmodel import select


import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from src.dependencies.database import SessionDep
from src.schemas.user import TokenData, UserInDB
from src.models.user import User

from config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    }
}


password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

# Create an instance of OAuth2PasswordBearer (A tool provided from FastAPI to use OAuth2 with the password flow using a bearer token) with the token URL set to "token" (This will just create a url for the user to use to get the access token by sending the token and type bearer in the request's Authorization header).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


# # Create a function called get_user that will receive the db and username as arguments and return a user object if the user exists in the db, otherwise it will return None.
# def get_user(db, username: str):
#     if username in db:
#         # Create a user object by getting the user dictionary from the db using the username as the key.
#         user_dict = db[username]
#         # Use the UserInDB class to create a user object by unpacking the user dictionary using the ** operator and passing it to the UserInDB class. The ** operator will unpack the dictionary and pass the key-value pairs as keyword arguments to the UserInDB class.
#         return UserInDB(**user_dict)


def get_user_from_db(user, session: SessionDep):
    db_user = session.exec(select(User).where(User.username == user)).first()
    return db_user


# Create a function called authenticate_user that will receive the fake_db, username, and password as arguments to pass them to the get_user function.
def authenticate_user(username, password, session):
    # Create a user object by calling the get_user function and passing the fake_db and username as arguments. The get_user function will check if the user exists in the fake_db and return a user object if it does, otherwise it will return False.
    user = get_user_from_db(username, session)

    # If the user does not exist, verify the password against a dummy hash to mitigate timing attacks and return False.
    if not user:
        verify_password(password, DUMMY_HASH)
        return False

    # If the user exists, verify the password against the hashed password stored in the user object. If the password is incorrect, return False.
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Create a function called create_access_token that receives and data dic and the expiration_delta from the login function in user_services
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # Create an object to store a copy of the data to prevent overwriting it
    to_encode = data.copy()
    # Check if a time delta is provided and use it to create an object called expire to set the expire time to be an amount of time (set in the secret expire time) from the time of the token creation
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    # create a default expire time set to 15 minutes from the time of the token creation
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    # Update the to_encode dictionary with the expire time set as a key-value pair with "exp" as the key and the expire object as the value
    to_encode.update({"exp": expire})
    # Create an object called encoded_jwt that will use the jwt module to create a JWT style access token by encoding the data from the to_encode object using the secret encoding key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Create a function called get_current_user that will get the token from the Token dependency and decode it to get the username from the token to use it to get the username from the database
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # try to create a payload object by decoding the token (created on logging in) using the secret decoding key and algorithm
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Get the user name from the key "sub" in the token dictionary
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    username = token_data.username
    user = get_user_from_db(username, session)
    # user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Create a function called get_current_active_user that returns a current_user object that's a User object with the get_current_user dependency
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    # Check if the user state is disabled (set to True)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
