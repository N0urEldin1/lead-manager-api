from pydantic import BaseModel
Base = BaseModel


class Lead(Base):
    name: str
    company: str
    email: str
    status: str
