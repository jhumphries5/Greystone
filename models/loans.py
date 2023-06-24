from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.db import Base
from pydantic import BaseModel

class Loan(Base):
    __tablename__ = "loans"

    id : int = Column(Integer, primary_key=True, index=True)

    amount : float = Column(Float)
    apr : float = Column(Float)
    term : int = Column(Integer)
    status : str = Column(String)
    owner_id : int = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="loans")
    users = relationship("User", secondary="loan_access", back_populates="shared_loans")

class LoanSchemaBase(BaseModel):
    amount: float
    apr: float
    term: int
    status: str = "active"
    owner_id: int

class LoanSchema(LoanSchemaBase):
    id: int

    class Config:
        orm_mode = True

class LoanScheduleSchema(BaseModel):
    month: int
    open_balance: float
    total_payment: float
    principal_payment: float
    interest_payment: float
    close_balance: float

class LoanSummarySchema(BaseModel):
    current_principal: float
    aggregate_principal_paid: float
    aggregate_interest_paid: float

class LoanAccess(Base):
    __tablename__ = "loan_access"

    loan_id = Column(Integer, ForeignKey('loans.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)