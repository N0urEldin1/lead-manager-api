from fastapi import Depends
# USe the sqlmodel to imports the SQLModel library to provide the ORM functionality for FastAPI
from sqlmodel import Session, SQLModel, create_engine, select
from typing import Annotated

# Create a variable to hold the database filename
sqlite_file_name = "database.db"
# Create a variable to create the URL that will be used to connect with the database
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
# Create the engine object using the create_engine method from sqlmodel
# Pass the url you've just created as a parameter
engine = create_engine(sqlite_url, connect_args=connect_args)

# Define a function that when called, will run the create_all method with engine as the parameter to create the database file and the table


def create_db_and_tables():
    # Use SQLModel class attribute metadata (that's created as an instance of a class MetaData) to access the Table Model class you created
    # Use the method create_all on the Table Model passing the engine so it can create the database and setup the table using the Table Model
    SQLModel.metadata.create_all(engine)

# Create a function that will be used as a FastAPI dependency


def get_session():
    # Create a session using the Session class with the engine as an parameter
    # Use "with" to context manage the session you're creating and use yield to allow the endpoint to work on it and finish the it will return to here to get closed
    with Session(engine) as session:
        yield session


# Create a variable called SessionDep to later be used as a dependency
# Annotated is creating and adding the session dependency to the class Session
# Annotated is saying that whenever SessionDep is called, any object that will be created using the class Session will need to use (depends on) get_session
SessionDep = Annotated[Session, Depends(get_session)]
