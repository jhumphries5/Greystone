from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import loans, users
from controllers import UserController
from controllers import LoanController
from database.db import get_db

router = APIRouter(tags=["Users"])


@router.post("/users", response_model=users.UserSchema)
def create_user(userData: users.UserSchemaBase, db: Session = Depends(get_db)):
    """
    Creates a new user
    """
    err = UserController.validate_user(db, userData)
    if err:
        raise err

    return UserController.create_user(db=db, userData=userData)

@router.get("/users", response_model=List[users.UserSchema])
def list_users(db: Session = Depends(get_db)):
    """
    Lists all existing users
    """
    return UserController.get_users(db=db)

@router.get("/users/{user_id}/loans", response_model=List[loans.LoanSchema])
def list_user_loans(user_id: int, db: Session = Depends(get_db)):
    """
    List all loans a user has access to
    This includes loans both owned by and shared with the user
    """
    user = UserController.get_user_by_id(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User %d not found" % user_id )

    return LoanController.get_loans_by_user_id(db=db, user_id=user_id)
