from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db_session import get_session
from models.exception import Exception as ExceptionModel
from schemas.exception import ExceptionCreate, ExceptionOut
from schemas.transitions import AssignIn, TransitionIn, ApprovalIn
from services.exceptions import assign_exception, transition_exception, approve_exception

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

@router.post("/{exc_id}/assign", response_model=ExceptionOut)
def assign(exc_id: int, payload: AssignIn, db: Session = Depends(get_session)):
    return assign_exception(db, exc_id, payload.assigned_to, payload.actor_id, payload.comment)

@router.post("/{exc_id}/transition", response_model=ExceptionOut)
def transition(exc_id: int, payload: TransitionIn, db: Session = Depends(get_session)):
    return transition_exception(db, exc_id, payload.to_status.upper(), payload.actor_id, payload.comment)

@router.post("/{exc_id}/approve", response_model=ExceptionOut)
def approve(exc_id: int, payload: ApprovalIn, db: Session = Depends(get_session)):
    return approve_exception(db, exc_id, payload.level, payload.decision, payload.approver_id, payload.comment)
