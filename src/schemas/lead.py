from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from src.models.lead import LeadBase


class LeadPublic(LeadBase):  # Create a data model with lead_id set to int only (without | None) to be used as a response model that indicate we always return a lead is
    lead_id: int


class LeadResponse(BaseModel):
    data: LeadPublic


class PaginationData(SQLModel):  # Create a data model for the pagination data response
    page: int
    page_size: int
    item_count: int


# Create a data model to be used as the response model for requesting paginated data
# Set data to inherit from the base model to represent the lead data
# # Set pagination to inherit from pagination data to represent the page, page_size, and item_count data
class PaginatedPublic(SQLModel):
    data: list[LeadPublic]
    pagination: PaginationData
    next_page: str | None = Field(default=None)
    previous_page: str | None = Field(default=None)


# class PaginatedResponse(BaseModel):
#     data: PaginatedPublic
