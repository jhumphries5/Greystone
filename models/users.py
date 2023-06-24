from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.db import Base
from pydantic import BaseModel

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    loans = relationship("Loan", back_populates="owner")
    shared_loans = relationship("Loan", secondary="loan_access", back_populates="users")

class UserSchemaBase(BaseModel):
    username: str

class UserSchema(UserSchemaBase):
    id: int

    class Config:
        orm_mode = True
