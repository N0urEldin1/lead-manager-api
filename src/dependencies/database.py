from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

from src.database.db import get_session

# Create a variable called SessionDep to later be used as a dependency
SessionDep = Annotated[Session, Depends(get_session)]
