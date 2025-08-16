from typing import Optional
from pydantic import BaseModel

class AssignIn(BaseModel):
    assigned_to: int
    actor_id: Optional[int] = None
    comment: Optional[str] = None

class TransitionIn(BaseModel):
    to_status: str
    actor_id: Optional[int] = None
    comment: Optional[str] = None

class ApprovalIn(BaseModel):
    level: int = 1
    decision: str  # "APPROVED" or "REJECTED"
    approver_id: int
    comment: Optional[str] = None
