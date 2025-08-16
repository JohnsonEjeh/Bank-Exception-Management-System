from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_session import get_session
from models.exception_type import ExceptionType
from schemas.exception_type import ExceptionTypeCreate, ExceptionTypeOut

router = APIRouter(prefix="/exception-types", tags=["exception-types"])

@router.post("", response_model=ExceptionTypeOut, status_code=status.HTTP_201_CREATED)
def create_exception_type(payload: ExceptionTypeCreate, db: Session = Depends(get_session)):
    obj = ExceptionType(**payload.dict())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Exception type code already exists")
    db.refresh(obj)
    return obj

@router.get("", response_model=List[ExceptionTypeOut])
def list_exception_types(db: Session = Depends(get_session)):
    return db.query(ExceptionType).order_by(ExceptionType.id).all()
