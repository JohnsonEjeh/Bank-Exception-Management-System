from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_session import get_session
from models.user import User
from schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_session)):
    obj = User(**payload.dict())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="username/email already exists")
    db.refresh(obj)
    return obj

@router.get("", response_model=List[UserOut])
def list_users(db: Session = Depends(get_session)):
    return db.query(User).order_by(User.id).all()
