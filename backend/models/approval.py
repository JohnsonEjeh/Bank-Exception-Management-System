from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, SmallInteger, String, Text, DateTime, ForeignKey, Index
from .base import Base, TimestampMixin

class Approval(Base, TimestampMixin):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exception_id: Mapped[int] = mapped_column(ForeignKey("exceptions.id", ondelete="CASCADE"), index=True)
    level: Mapped[int] = mapped_column(SmallInteger)
    approver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    decision: Mapped[str] = mapped_column(String(16), default="PENDING", server_default="PENDING")
    comment:  Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

Index("ix_approvals_exception_level", Approval.exception_id, Approval.level)
