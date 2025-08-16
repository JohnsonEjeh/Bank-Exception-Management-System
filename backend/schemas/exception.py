from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ExceptionCreate(BaseModel):
    type_id: int
    title: str
    description: Optional[str] = None
    severity: Optional[str] = None
    bu_id: Optional[str] = None
    created_by: Optional[int] = None
    assigned_to: Optional[int] = None
    due_at: Optional[datetime] = None
    priority: Optional[int] = None

class ExceptionOut(BaseModel):
    id: int
    type_id: int
    title: str
    description: Optional[str]
    severity: Optional[str]
    bu_id: Optional[str]
    created_by: Optional[int]
    assigned_to: Optional[int]
    status: str
    priority: Optional[int]
    due_at: Optional[datetime]
    escalated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
