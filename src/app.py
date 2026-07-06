from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from src.lead import *
from src.db import *
from random import randint

from src.db import *

# start "project 2 scope.txt"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Lead)).first():
            session.add_all([
                Lead(lead_id=1, name="Ali", company="Tesla",
                     email="ali@tesla.com", status="New lead"),
                Lead(lead_id=2, name="Ahmed", company="Apple", email="ahmed@apple.com", status="New lead")]
            )
            session.commit()
    yield

app = FastAPI(root_path="/api/v1", lifespan=lifespan)


@app.get("/")
async def root():
    return "Welcome to the Lead Manager API!"


@app.get("/leads", response_model=Response[list[Lead]])
async def read_leads(session: SessionDep):
    data = session.exec(select(Lead)).all()
    return {"data": data}


@app.get("/leads/{lead_id}", response_model=Response[Lead])
async def read_lead(lead_id: int, session: SessionDep):
    data = session.get(Lead, lead_id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data": data}


@app.post("/leads", status_code=201)
async def create_lead(lead: Lead, session: SessionDep):

    new = {
        "lead_id": randint(100, 200),
        "name": lead.name,
        "company": lead.company,
        "email": lead.email,
        "status": lead.status}

    new = session.add_all(Lead(
        lead_id=1, name="Ali", company="Tesla", email="ali@tesla.com", status="New lead"))
    session.commit()

    return {"leads": new}


# @app.delete("/leads/{lead_id}")
# async def delete_lead(lead_id: int, session: SessionDep):
#     data = session.exec(select(Lead)).all()
#     for i, lead in enumerate(data):
#         if lead.get("lead_id") == lead_id:
#             data.pop(i)
#             return Response(status_code=204)
#     raise HTTPException(status_code=404)


# @app.put("/leads/{lead_id}")
# async def update_lead(lead_id: int, lead: Lead, session: SessionDep):
#     data = session.exec(select(Lead)).all()
#     updated = {
#         "lead_id": lead_id,
#         "name": lead.name,
#         "company": lead.company,
#         "email": lead.email,
#         "status": lead.status}

#     for i, lead in enumerate(data):
#         if lead.get("lead_id") == lead_id:
#             data[i] = updated
#             return {"leads": updated}
#     raise HTTPException(status_code=404)
