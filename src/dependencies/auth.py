from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.security import get_current_active_user, oauth2_scheme
from src.models.user import User

# Annotated is creating and adding the session dependency to the class Session
# Annotated is saying that whenever SessionDep is called, any object that will be created using the class Session will need to use (depends on) get_session

# Use the Annotated class to create a new type called UserDep that's creates a user object using the get_current_active_user from auth.security as a dependency to create the object
UserDep = Annotated[User, Depends(get_current_active_user)]
# Use the Annotated class to create a new type called TokenDep that is a string and depends on the oauth2_scheme dependency (which is an instance of OAuth2PasswordBearer) to get the token from the request header and pass it to the function that uses this dependency.
TokenDep = Annotated[str, Depends(oauth2_scheme)]
# Use the Annotated class to create a new type called FormDep that is an instance of OAuth2PasswordRequestForm and depends on the Depends class to get the form data from the request body and pass it to the function that uses this dependency.
FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
