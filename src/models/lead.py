from sqlmodel import Field, SQLModel


class LeadBase(SQLModel):  # Create a base data model using SQLModel with out setting table to true
    name: str
    company: str
    email: str
    status: str


# Create a class the inherits form the base data model and set table to True to create a Table model
# Inheriting from the class LeadBase and passing (table=True) will register the table definition in Lead's metadata attribute to be added to the data base as row


class Lead(LeadBase, table=True):
    # Use the Field function from sqlmodel to set arguments for columns
    # Create a lead_id row that could be int or None and set it's default value to None and make it the primary key (The unique identifier of each row in the table)
    # The lead_id column most be defaulted to None so that when you create a new instance of it, you wont assign a value to it to let the database create the id for you
    lead_id: int | None = Field(default=None, primary_key=True, index=True)
    owner_id: int | None = Field(
        default=None, foreign_key="user.user_id", index=True)


class LeadCreate(LeadBase):  # Create a separate data model using the base model to separate the request model for the data required for creating a lead (future proofing)
    pass


class LeadUpdate(LeadBase):  # Create a separate data model using the base model to separate the request model for the data required for updating a lead (future proofing)
    pass


# Create a separate data model to be a request model and set every type to be optional to allow users to update only the data they want
class LeadPatch(SQLModel):
    name: str | None = Field(default=None)
    company: str | None = Field(default=None)
    email: str | None = Field(default=None)
    status: str | None = Field(default=None)
