from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from src.lead import Lead
from random import randint

from src.db import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(root_path="/api/v1", lifespan=lifespan)

leads = [{"lead_id": 1, "name": "Ali", "company": "Tesla", "email": "ali@gmail.com", "status": "status"},
         {"lead_id": 2, "name": "Ahmed", "company": "Apple",
          "email": "email", "status": "status"},
         {"lead_id": 3, "name": "Mohamed", "company": "PayPal",
          "email": "email", "status": "status"},
         {"lead_id": 4, "name": "Nour", "company": "FastAPI",
          "email": "email", "status": "status"},
         {"lead_id": 5, "name": "Omar", "company": "Instagram",
          "email": "email", "status": "status"},
         {"lead_id": 6, "name": "Ola", "company": "Facebook",
          "email": "email", "status": "status"},
         {"lead_id": 7, "name": "Hagar", "company": "YouTube",
          "email": "email", "status": "status"},
         {"lead_id": 8, "name": "Jack", "company": "Reddit",
          "email": "email", "status": "status"},
         {"lead_id": 9, "name": "Joe", "company": "Mojang",
          "email": "email", "status": "status"},
         {"lead_id": 10, "name": "Othman", "company": "Stripe",
          "email": "email", "status": "status"},
         ]


@app.get("/")
async def root():
    return "Welcome to the Lead Manager API!"


@app.get("/leads")
async def read_leads():
    return {"leads": leads}


@app.get("/leads/{lead_id}")
async def read_lead(lead_id: int):
    for item in leads:
        if item.get("lead_id") == lead_id:
            return {"leads": item}
    raise HTTPException(status_code=404)


@app.post("/leads", status_code=201)
async def create_lead(lead: Lead):
    # new = {
    #     "lead_id": randint(100, 200),
    #     "data": {"name": lead.name,
    #              "company": lead.company,
    #              "email": lead.email,
    #              "status": lead.status}}

    new = {
        "lead_id": randint(100, 200),
        "name": lead.name,
        "company": lead.company,
        "email": lead.email,
        "status": lead.status}

    leads.append(new)
    return {"leads": new}


@app.delete("/leads/{lead_id}")
async def delete_lead(lead_id: int):
    for i, lead in enumerate(leads):
        if lead.get("lead_id") == lead_id:
            leads.pop(i)
            return Response(status_code=204)
    raise HTTPException(status_code=404)


@app.put("/leads/{lead_id}")
async def update_lead(lead_id: int, lead: Lead):
    updated = {
        "lead_id": lead_id,
        "name": lead.name,
        "company": lead.company,
        "email": lead.email,
        "status": lead.status}

    for i, lead in enumerate(leads):
        if lead.get("lead_id") == lead_id:
            leads[i] = updated
            return {"leads": updated}
    raise HTTPException(status_code=404)
