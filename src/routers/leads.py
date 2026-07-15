from fastapi import Query, Request, APIRouter
from sqlalchemy import select

from src.dependencies.database import SessionDep
from src.models.lead import Lead, LeadCreate, LeadPatch, LeadUpdate
from src.schemas.lead import LeadResponse, PaginatedPublic, LeadPublic
from src.utils.http404 import error
from src.services import lead_services

router = APIRouter()


# Create a GET endpoint to get all leads form the database
@router.get("/leads", response_model=PaginatedPublic)
# Pass the request parameter to access the request url, the session dependency, the name, company, and status as query parameters to handle filtering
# Pass the page and page size query parameter and use the Query function to set a default and validation
async def read_leads(request: Request, session: SessionDep, name: str | None = None, company: str | None = None, status: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(10, ge=5)):
    return lead_services.read_all(request, session, name, company, status, page, page_size)


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def read_lead(lead_id: int, session: SessionDep):
    return lead_services.read(lead_id, session)


@router.post("/leads", status_code=201, response_model=LeadPublic)
# Use the type annotation LeadCreate (a class in lead.py) to
async def create_lead(lead: LeadCreate, session: SessionDep):
    return lead_services.create(lead, session)


@router.delete("/leads/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, session: SessionDep):
    return lead_services.delete(lead_id, session)


@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: int, lead: LeadUpdate, session: SessionDep):
    return lead_services.update(lead_id, lead, session)


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: int, lead: LeadPatch, session: SessionDep):
    return lead_services.patch(lead_id, lead, session)
