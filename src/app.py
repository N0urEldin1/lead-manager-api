from fastapi import FastAPI, HTTPException, Response
from src.lead import Lead
from random import randint

app = FastAPI(root_path="/api/v1")

# leads = [{"lead_id": 1, "data": {"name": "Ali", "company": "Tesla", "email": "ali@gmail.com", "status": "status"}},
#          {"lead_id": 2, "data": {"name": "Ahmed", "company": "Apple",
#                                  "email": "email", "status": "status"}},
#          {"lead_id": 3, "data": {"name": "Mohamed", "company": "PayPal",
#                                  "email": "email", "status": "status"}},
#          {"lead_id": 4, "data": {"name": "Nour", "company": "FastAPI",
#                                  "email": "email", "status": "status"}},
#          {"lead_id": 5, "data": {"name": "Omar", "company": "Instagram",
#                                  "email": "email", "status": "status"}},
#          {"lead_id": 6, "data": {"name": "Ola", "company": "Facebook",
#                                  "email": "email", "status": "status"}},
#          {"lead_id": 7, "data": {"name": "Hagar", "company": "YouTube",
#                                  "email": "email", "status": "status"}},
#          {"lead_id": 8, "data": {"name": "Jack", "company": "Reddit",
#                                  "email": "email", "status": "status"}},
#          {"lead_id": 9, "data": {"name": "Joe", "company": "Mojang",
#                                  "email": "email", "status": "status"}},
#          {"lead_id": 10, "data": {"name": "Othman", "company": "Stripe",
#                                   "email": "email", "status": "status"}},
#          ]

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


@app.post("/leads")
async def create_lead(lead: Lead):
    new = {
        "lead_id": randint(100, 200),
        "data": {"name": lead.name,
                 "company": lead.company,
                 "email": lead.email,
                 "status": lead.status}}

    leads.append(new)
    return {"leads": new}


@app.delete("/leads/{lead_id}")
async def delete_lead(lead_id: int):
    for i, lead in enumerate(leads):
        if lead.get("lead_id") == lead_id:
            leads.pop(i)
            return Response(status_code=204)
    raise HTTPException(status_code=404)
