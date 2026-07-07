from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from typing import Generic, TypeVar


class Lead(SQLModel, table=True):
    lead_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    company: str | None = Field(default=None)
    email: str
    status: str


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    data: T


class LeadCreate(SQLModel):
    lead_id: int | None
    name: str
    company: str
    email: str
    status: str


class LeadUpdate(SQLModel):
    name: str
    company: str
    email: str
    status: str


class LeadPatch(SQLModel):
    name: str | None = Field(default=None)
    company: str | None = Field(default=None)
    email: str | None = Field(default=None)
    status: str | None = Field(default=None)
