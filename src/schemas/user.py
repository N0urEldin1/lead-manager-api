from pydantic import BaseModel

from src.models.user import User, UserBase


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# class User(UserBase):
#     pass


class UserInDB(User):
    hashed_password: str
