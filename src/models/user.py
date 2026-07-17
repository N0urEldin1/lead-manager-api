from sqlmodel import Field, SQLModel


class UserBase(SQLModel):  # Create a base data model using SQLModel with out setting table to true
    username: str
    email: str | None = None
    full_name: str | None = None


# Create a class the inherits form the base data model and set table to True to create a Table model
class User(UserBase, table=True):
    # Use the Field function from sqlmodel to set arguments for columns
    user_id: int | None = Field(default=None, primary_key=True, index=True)
    disabled: bool | None = None
    is_superuser: bool = False
    hashed_password: str

# class UserCreate(UserBase):  # Create a separate data model using the base model to separate the request model for the data required for creating a user (future proofing)
#     # Create a user_id row that could be int or None and set it's default value to None and make it the primary key (The unique identifier of each row in the table)
#     # The user_id column most be defaulted to None so that when you create a new instance of it, you wont assign a value to it to let the database create the id for you
#     hashed_password: str


class UserRegister(SQLModel):  # Create a separate data model using the base model to separate the request model for the data required for creating a user (future proofing)
    username: str
    email: str | None = None
    full_name: str | None = None
    password: str
