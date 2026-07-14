from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from src.database.db import get_session
from src.routers.auth import get_current_active_user, oauth2_scheme
from src.models.user import User

# Create a variable called SessionDep to later be used as a dependency
# Annotated is creating and adding the session dependency to the class Session
# Annotated is saying that whenever SessionDep is called, any object that will be created using the class Session will need to use (depends on) get_session
SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[User, Depends(get_current_active_user)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
