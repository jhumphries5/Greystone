from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import loans
from controllers import LoanController, UserController
from database.db import get_db

router = APIRouter(tags=["Loans"])


@router.post("/loans", response_model=loans.LoanSchema)
def create_loan(loanData: loans.LoanSchemaBase, db: Session = Depends(get_db)):
    """
    Route to create a new loan
    Adds the owner to the loan access map
    """
    err = LoanController.validateLoan(loanData)
    if err:
        raise err

    owner = UserController.get_user_by_id(db=db, id=loanData.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="User %d not found" % loanData.owner_id )

    loan = LoanController.create_loan(db=db, loanData=loanData)
    LoanController.add_user(db=db, loan_id=loan.id, user_id=loanData.owner_id)

    return loan

@router.get("/loans/{loan_id}", response_model=List[loans.LoanScheduleSchema])
def get_loan_schedule(loan_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Route to return the full monthly loan schedule
    The loan must be owned by or shared with the user
    """
    # Maybe better to make these failed auth checks return 404s? To obfuscate the real IDs
    if not LoanController.access_check(db=db, loan_id=loan_id, user_id=user_id):
        raise HTTPException(status_code=403, detail="User %d does not have access to loan %d" % (user_id, loan_id) )

    loan = LoanController.get_loan_by_id(db=db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan %d not found" % loan_id )

    return LoanController.get_loan_schedule_for_loan(loan)

@router.get("/loans/{loan_id}/month/{month}", response_model=loans.LoanSummarySchema)
def get_loan_summary(loan_id: int, month: int, user_id: int, db: Session = Depends(get_db)):
    """
    Route to return the loan summary for a given month
    The loan must be owned by or shared with the user
    """
    if not LoanController.access_check(db=db, loan_id=loan_id, user_id=user_id):
        raise HTTPException(status_code=403, detail="User %d does not have access to loan %d" % (user_id, loan_id) )

    loan = LoanController.get_loan_by_id(db=db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan %d not found" % loan_id )

    try:
        return LoanController.get_loan_summary_for_loan(loan, month)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/loans/{loan_id}", response_model=loans.LoanSchema)
def update_loan(loan_id: int, loan_data: loans.LoanSchemaBase, user_id: int, db: Session = Depends(get_db)):
    """
    Updates the loan at the provided loan_id with the new loan_data
    The loan must be owned by the user at user_id
    """
    err = LoanController.validateLoan(loan_data)
    if err:
        raise err

    loan = LoanController.get_loan_by_id(db=db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan %d not found" % loan_id )

    if not user_id == loan.owner_id:
        raise HTTPException(status_code=403, detail="User %d does not have access to update loan %d" % (user_id, loan_id) )

    return LoanController.update_loan(db=db, loan=loan, loanData=loan_data)

@router.post("/loans/{loan_id}/share")
def share_loan(loan_id: int, owner_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Route to share a loan with a user at user_id
    The loan must be owned by the user at owner_id
    """
    loan = LoanController.get_loan_by_id(db=db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan %d not found" % loan_id )

    user = UserController.get_user_by_id(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User %d not found" % user_id )

    if loan.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="User %d does not own loan %d" % (owner_id, loan_id) )

    return {"success"} if LoanController.add_user(db=db, loan_id=loan_id, user_id=user_id) else {"failure"}