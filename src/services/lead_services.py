from sqlalchemy import select
from fastapi import Query, Request, APIRouter
from src.models.lead import Lead, LeadBase
from src.schemas.lead import LeadPublic
from src.utils.http404 import error


def read_all(request, session, name, company, status, page, page_size):
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
    data = session.scalars(statement.order_by(
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
            "page_size": page_size,
            "item_count": len(data),
        },
        "next_page": next_url,
        "previous_page": prev_url
    }


def read(lead_id, session):
    data = session.get(Lead, lead_id)
    if not data:
        error()
    return {"data": data}


def create(lead, session):
    # create an instance of Lead (the table model) using model_validate to pass the lead object (an instance of LeadCreate) to read it's attributes
    db_lead = Lead.model_validate(lead)

    session.add(db_lead)
    session.commit()
    session.refresh(db_lead)
    return db_lead


def delete(lead_id, session):
    data = session.get(Lead, lead_id)
    if not data:
        error()
    session.delete(data)
    session.commit()


def update(lead_id, lead, session):
    data = session.get(Lead, lead_id)
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


def patch(lead_id, lead, session):
    data = session.get(Lead, lead_id)
    if not data:
        error()
    new_data = lead.model_dump(exclude_unset=True)
    for key, value in new_data.items():
        setattr(data, key, value)
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}
