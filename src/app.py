# Imports the async context manager decorator from the contextlib module
from contextlib import asynccontextmanager


# Use the fastapi module (From the FastAPI lib) to import the FastAPI class (that inherits from Starlette) to provides the API functionality alongside the HTTPException class to handle returning HTTP errors
from fastapi import FastAPI
from sqlalchemy import select
from src.models.lead import Lead
from src.database.db import create_db_and_tables, engine, Session
from src.routers import leads, users


@asynccontextmanager  # Use the async context manager decorator to turn the lifespan generator function into an asynchronous context manager so the lifespan function will run on startup and close on shutdown
# generator function turned into asynchronous generator function
# Use this asynchronous generator function to handle FastAPI lifespan (creating the database and table and database seeding on startup and handle shutdown)
async def lifespan(app: FastAPI):
    # Calls the function that will create the database and table if they don't exist yet
    create_db_and_tables()
    # Use the context manager to open a session
    with Session(engine) as session:
        # Checks if when executing getting the first row from the Lead table returns None
        if not session.exec(select(Lead)).first():
            # If none, uses the session to add two rows (Database seeding)
            session.add_all([
                Lead(lead_id=1, name="Ali", company="Tesla",
                     email="ali@tesla.com", status="New lead"),
                Lead(lead_id=2, name="Ahmed", company="Apple", email="ahmed@apple.com", status="New lead")]
            )
            session.commit()
    # Use yield to pause here while the application is running.
    yield


# Create an app object that's instance of FastAPI with a predefined root path and set it's lifespan parameter to use the lifespan function on startup and shutdown
app = FastAPI(root_path="/api/v1", lifespan=lifespan)


app.include_router(leads.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return "Welcome to the Lead Manager API!"
