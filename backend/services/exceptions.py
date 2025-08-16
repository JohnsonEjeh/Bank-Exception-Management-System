from typing import Optional, Dict, Any
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.exception import Exception as ExceptionModel
from models.audit_event import AuditEvent
from models.approval import Approval

ALLOWED_STATUSES = {
    "NEW",
    "TRIAGED",
    "IN_PROGRESS",
    "AWAITING_APPROVAL",
    "APPROVED",
    "REJECTED",
    "RESOLVED",
    "CLOSED",
    "ESCALATED",
}

# Very simple allowed transitions for now
TRANSITIONS = {
    "NEW": {"TRIAGED", "IN_PROGRESS", "AWAITING_APPROVAL"},
    "TRIAGED": {"IN_PROGRESS", "AWAITING_APPROVAL"},
    "IN_PROGRESS": {"AWAITING_APPROVAL", "RESOLVED"},
    "AWAITING_APPROVAL": {"APPROVED", "REJECTED"},
    "APPROVED": {"RESOLVED"},
    "REJECTED": {"IN_PROGRESS", "CLOSED"},
    "RESOLVED": {"CLOSED"},
    "ESCALATED": {"IN_PROGRESS", "AWAITING_APPROVAL"},
    "CLOSED": set(),
}

def _audit(
    db: Session,
    actor_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: int,
    old: Optional[Dict[str, Any]],
    new: Optional[Dict[str, Any]],
) -> None:
    ev = AuditEvent(
        at=datetime.now(timezone.utc),
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old=old,
        new=new,
    )
    db.add(ev)

def _get_exception(db: Session, exc_id: int) -> ExceptionModel:
    obj = db.get(ExceptionModel, exc_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exception not found")
    return obj

def assign_exception(
    db: Session, exc_id: int, assigned_to: int, actor_id: Optional[int], comment: Optional[str]
) -> ExceptionModel:
    obj = _get_exception(db, exc_id)
    old = {"assigned_to": obj.assigned_to}
    obj.assigned_to = assigned_to
    db.flush()
    _audit(
        db,
        actor_id=actor_id,
        action="ASSIGNED",
        entity_type="exception",
        entity_id=obj.id,
        old=old,
        new={"assigned_to": obj.assigned_to, "comment": comment},
    )
    db.commit()
    db.refresh(obj)
    return obj

def transition_exception(
    db: Session, exc_id: int, to_status: str, actor_id: Optional[int], comment: Optional[str]
) -> ExceptionModel:
    if to_status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Unknown status")

    obj = _get_exception(db, exc_id)
    allowed = TRANSITIONS.get(obj.status, set())
    if to_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid transition {obj.status} -> {to_status}")

    old = {"status": obj.status}
    obj.status = to_status
    if to_status == "ESCALATED":
        obj.escalated_at = datetime.now(timezone.utc)

    db.flush()
    _audit(
        db,
        actor_id=actor_id,
        action="STATUS_CHANGED",
        entity_type="exception",
        entity_id=obj.id,
        old=old,
        new={"status": obj.status, "comment": comment},
    )
    db.commit()
    db.refresh(obj)
    return obj

def approve_exception(
    db: Session,
    exc_id: int,
    level: int,
    decision: str,
    approver_id: int,
    comment: Optional[str],
) -> ExceptionModel:
    decision = (decision or "").upper()
    if decision not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=400, detail="decision must be APPROVED or REJECTED")

    obj = _get_exception(db, exc_id)

    # maker-checker: creator cannot approve own exception (if creator known)
    if obj.created_by is not None and obj.created_by == approver_id:
        raise HTTPException(status_code=400, detail="Maker-checker violation: creator cannot approve")

    # record the approval
    ap = Approval(
        exception_id=obj.id,
        level=level,
        approver_id=approver_id,
        decision=decision,
        comment=comment,
        decided_at=datetime.now(timezone.utc),
    )
    db.add(ap)

    old = {"status": obj.status}
    if decision == "APPROVED":
        obj.status = "APPROVED"
    else:
        obj.status = "REJECTED"

    db.flush()

    _audit(
        db,
        actor_id=approver_id,
        action=f"APPROVAL_{decision}",
        entity_type="exception",
        entity_id=obj.id,
        old=old,
        new={"status": obj.status, "approval": {"level": level, "decision": decision, "comment": comment}},
    )

    db.commit()
    db.refresh(obj)
    return obj
