
from fastapi import APIRouter

from src.dependencies.auth import FormDep, TokenDep, UserDep
from src.schemas.user import Token, User
from src.services import user_services
router = APIRouter()


@router.get("/items/")
async def read_items(token: TokenDep):
    return {"token": token}


async def get_current_user(token: TokenDep):
    return user_services.get_current(token)


@router.post("/token")
async def login_for_access_token(form_data: FormDep) -> Token:
    return user_services.login(form_data)


@router.get("/users/me/")
async def read_users_me(
    current_user: UserDep,
) -> User:
    return current_user
