from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from typing import Generic, TypeVar

# Create a class the inherits form SQLModel and set table to True to create a Table model
# Inheriting from the class SQLModel and passing (table=True) will register the created(child) class in it's metadata attribute


class Lead(SQLModel, table=True):
    # Use the Field function from sqlmodel to set arguments for columns
    # Create a lead_id row that could be int or None and set it's default value to None and make it the primary key (The unique identifier of each row in the table)
    # The lead_id column most be defaulted to None so that when you create a new instance of it, you wont assign a value to it to let the database create the id for you
    lead_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    company: str
    email: str
    status: str


# Create a generic type hint to c
T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    data: T

# Create a class the inherits form SQLModel and do not set table to True to create a Data model


class LeadCreate(SQLModel):
    name: str
    company: str
    email: str
    status: str

# Create another data model


class LeadUpdate(SQLModel):
    name: str
    company: str
    email: str
    status: str

# Create another data model


class LeadPatch(SQLModel):
    name: str | None = Field(default=None)
    company: str | None = Field(default=None)
    email: str | None = Field(default=None)
    status: str | None = Field(default=None)
