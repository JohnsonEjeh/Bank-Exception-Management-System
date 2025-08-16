from typing import Optional
from pydantic import BaseModel

class ExceptionTypeCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    default_sla_hours: int = 72
    approval_levels: int = 1
    active: bool = True

class ExceptionTypeOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    default_sla_hours: int
    approval_levels: int
    active: bool

    class Config:
        from_attributes = True
