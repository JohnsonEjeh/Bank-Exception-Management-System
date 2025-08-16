from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db_session import get_session
from models.exception import Exception as ExceptionModel
from schemas.exception import ExceptionCreate, ExceptionOut

router = APIRouter(prefix="/exceptions", tags=["exceptions"])

@router.post("", response_model=ExceptionOut, status_code=201)
def create_exception(payload: ExceptionCreate, db: Session = Depends(get_session)):
    obj = ExceptionModel(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[ExceptionOut])
def list_exceptions(
    status: Optional[str] = None,
    type_id: Optional[int] = None,
    db: Session = Depends(get_session),
):
    q = db.query(ExceptionModel)
    if status:
        q = q.filter(ExceptionModel.status == status)
    if type_id:
        q = q.filter(ExceptionModel.type_id == type_id)
    return q.order_by(ExceptionModel.id.desc()).all()
