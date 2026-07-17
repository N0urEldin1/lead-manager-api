
from fastapi import APIRouter

from src.dependencies.auth import FormDep, TokenDep, UserDep
from src.schemas.user import Token, User, UserInDB
from src.services import user_services
router = APIRouter()


# Create a GET endpoint at the path "/items/" that will use the token dependency to access the /token url so the user can access the access token
@router.get("/items/")
async def read_items(token: TokenDep):
    return {"token": token}


# Create a POST endpoint at the path "/token" that the user will use to login by sending the username and password in the request body.
@router.post("/token")
# Create a function called login_for_access_token that will receive the form_data dependency (which is an instance of OAuth2PasswordRequestForm used to get the form data from the request body) and return a Token object (which is an instance of the Token class) that will be created by the login function from the user_services module.
async def login_for_access_token(form_data: FormDep) -> Token:
    # Use the login function the return a a token for the use to store for later interactions with the API.
    return user_services.login(form_data)


# Create a GET endpoint at the path "/users/me/" that the user will use to get their credentials
@router.get("/users/me/")
async def read_users_me(
    current_user: UserDep,
) -> User:  # Create a function called read_users_me that will use the UserDep to return a User object
    return current_user
