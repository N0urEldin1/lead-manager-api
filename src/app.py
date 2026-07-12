# Imports the async context manager decorator from the contextlib module
from contextlib import asynccontextmanager
from typing import Annotated

# Use the fastapi module (From the FastAPI lib) to import the FastAPI class (that inherits from Starlette) to provides the API functionality alongside the HTTPException class to handle returning HTTP errors
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from src.lead import Lead, LeadPublic, LeadCreate, LeadUpdate, LeadPatch, PaginatedResponse
from src.db import create_db_and_tables, engine, Session, select, SessionDep
from src.user import User, UserDep, TokenDep, FormDep, fake_users_db, UserInDB, fake_hash_password, fake_decode_token
from sqlmodel import func

from fastapi.encoders import jsonable_encoder


def error():
    status_code = 404
    raise HTTPException(status_code=status_code, detail={
        "status_code": status_code, "error_details": "Item does not exist"})

# Use the async context manager decorator to turn the lifespan generator function into an asynchronous context manager so the lifespan function will run on startup and close on shutdown


@asynccontextmanager
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


# @app.get("/users/me")
# async def get_current_user(current_user: UserDep):
#     return current_user


@app.get("/items/")
async def read_items(token: TokenDep):
    return {"token": token}


async def get_current_user(token: TokenDep):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: FormDep):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.get("/")
async def root():
    return "Welcome to the Lead Manager API!"

# Create a GET endpoint to get all leads form the database


@app.get("/leads", response_model=PaginatedResponse)
# Pass the request parameter to access the request url, the session dependency, the name, company, and status as query parameters to handle filtering
# Pass the page and page size query parameter and use the Query function to set a default and validation
async def read_leads(request: Request, session: SessionDep, name: str | None = None, company: str | None = None, status: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(10, ge=5)):

    # Initialize the query by selecting the table model
    statement = select(Lead)

    # Handle validation and add 'where's to the query if provided
    if name is not None:
        statement = statement.where(Lead.name == name)
    if company is not None:
        statement = statement.where(Lead.company == company)
    if status is not None:
        statement = statement.where(Lead.status == status)

    # Calculate the offset the multiplying the number of previous pages (pages to skip) by the number of items per page
    offset = (page - 1) * page_size
    # Fetch the matching data
    data = session.exec(statement.order_by(
        Lead.lead_id).offset(offset).limit(page_size)).all()

    # Create a base url for creating the next and previous page urls
    base_url = str(request.url).split("?")[0]

    # If the number of returned data is less then the page size asked for (meaning there's less data to return than asked for) don't return a url for next page
    if page_size > len(data):
        next_url = None
    else:
        next_url = f"{base_url}?page={page+1}&page_size={page_size}"

    # Only return a url for the previous page if the use is on page 2 or higher
    if page > 1:
        prev_url = f"{base_url}?page={page-1}&page_size={page_size}"
    else:
        prev_url = None

    return {
        "data": data,
        "pagination": {
            "page": page,
            "Page_size": page_size,
            "item_count": len(data),
        },
        "next_page": next_url,
        "previous_page": prev_url
    }


@app.get("/leads/{lead_id}", response_model=LeadPublic)
async def read_lead(lead_id: int, session: SessionDep):
    data = session.get(LeadPublic, lead_id)
    if not data:
        error()
    return {"data": data}


@app.post("/leads", status_code=201, response_model=LeadPublic)
# Use the type annotation LeadCreate (a class in lead.py) to
async def create_lead(lead: LeadCreate, session: SessionDep):
    # create an instance of Lead (the table model) using model_validate to pass the lead object (an instance of LeadCreate) to read it's attributes
    db_lead = Lead.model_validate(lead)

    session.add(db_lead)
    session.commit()
    session.refresh(db_lead)
    return {"data": db_lead}


@app.delete("/leads/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, session: SessionDep):
    data = session.get(LeadPublic, lead_id)
    if not data:
        error()
    session.delete(data)
    session.commit()


@app.put("/leads/{lead_id}", response_model=LeadPublic)
async def update_lead(lead_id: int, lead: LeadUpdate, session: SessionDep):
    data = session.get(LeadPublic, lead_id)
    if not data:
        error()
    data.name = lead.name
    data.company = lead.company
    data.email = lead.email
    data.status = lead.status
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}


@app.patch("/leads/{lead_id}", response_model=LeadPublic)
async def update_lead(lead_id: int, lead: LeadPatch, session: SessionDep):
    data = session.get(LeadPublic, lead_id)
    if not data:
        error()
    new_data = lead.model_dump(exclude_unset=True)
    print(new_data)
    for key, value in new_data.items():
        setattr(data, key, value)
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}
