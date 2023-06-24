from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.users import UserSchemaBase, User

class UserController:

    @staticmethod
    def validate_user(db: Session, userData: UserSchemaBase):
        '''
        Validate the input data for user creation
        Returns:
            HTTPException if validation fails
            None otherwise
        '''
        if not isinstance(userData.username, str):
            return HTTPException(status_code=422, detail="Username must be a string" )
        if len(userData.username) < 3:
            return HTTPException(status_code=422, detail="Username must be at least 3 characters")
        if UserController.get_user_by_username(db, userData.username) is not None:
            return HTTPException(status_code=409, detail="Username already exists")
        return None

    @staticmethod
    def create_user(db: Session, userData: UserSchemaBase):
        db_user = User(**userData.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_id(db: Session, id: int):
        return db.query(User).filter(User.id == id).first()

    @staticmethod
    def get_user_by_username(db: Session, username:str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_users(db: Session, skip: int=0, limit: int=100):
        return db.query(User).offset(skip).limit(limit).all()