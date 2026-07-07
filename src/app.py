from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from src.lead import Lead, LeadCreate, LeadUpdate, LeadPatch, Response
from src.db import create_db_and_tables, engine, Session, select, SessionDep

from fastapi.encoders import jsonable_encoder

# cd programing; start "project 2 scope.txt"


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


# @app.get("/leads", response_model=Response[list[Lead]])
# async def read_leads(session: SessionDep, status: str | None = None):
#     if status is not None:
#         statement = select(Lead).where(Lead.status == status)
#         results = session.exec(statement)
#         return {"data": results}
#     data = session.exec(select(Lead)).all()
#     return {"data": data}

@app.get("/leads", response_model=Response[list[Lead]])
async def read_leads(session: SessionDep, name: str | None = None, company: str | None = None, status: str | None = None):
    statement = select(Lead)
    if name is not None:
        statement = statement.where(Lead.name == name)
    if company is not None:
        statement = statement.where(Lead.company == company)
    if status is not None:
        statement = statement.where(Lead.status == status)
    data = session.exec(statement).all()
    return {"data": data}


@app.get("/leads/{lead_id}", response_model=Response[Lead])
async def read_lead(lead_id: int, session: SessionDep):
    data = session.get(Lead, lead_id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data": data}


@app.post("/leads", status_code=201, response_model=Response[Lead])
async def create_lead(lead: LeadCreate, session: SessionDep):
    db_lead = Lead.model_validate(lead)

    session.add(db_lead)
    session.commit()
    session.refresh(db_lead)
    return {"data": db_lead}


@app.delete("/leads/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, session: SessionDep):
    data = session.get(Lead, lead_id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()


@app.put("/leads/{lead_id}", response_model=Response[Lead])
async def update_lead(lead_id: int, lead: LeadUpdate, session: SessionDep):
    data = session.get(Lead, lead_id)
    if not data:
        raise HTTPException(status_code=404)
    data.name = lead.name
    data.company = lead.company
    data.email = lead.email
    data.status = lead.status
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}


@app.patch("/leads/{lead_id}", response_model=Response[Lead])
async def update_lead(lead_id: int, lead: LeadPatch, session: SessionDep):
    data = session.get(Lead, lead_id)
    if not data:
        raise HTTPException(status_code=404)
    new_data = lead.model_dump(exclude_unset=True)
    print(new_data)
    for key, value in new_data.items():
        setattr(data, key, value)
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}

    # for key in new_data:
    #     if key == "name":
    #         data.name = lead.name
    #     elif key == "company":
    #         data.company = lead.company
    #     elif key == "email":
    #         data.email = lead.email
    #     elif key == "status":
    #         data.status = lead.status
