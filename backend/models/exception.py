from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, SmallInteger
from .base import Base, TimestampMixin

class Exception(Base, TimestampMixin):
    __tablename__ = "exceptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    type_id: Mapped[int] = mapped_column(ForeignKey("exception_types.id", ondelete="RESTRICT"), index=True)
    title:   Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity:    Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    bu_id:       Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_by:  Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    status:   Mapped[str] = mapped_column(String(32), index=True, default="NEW", server_default="NEW")
    priority: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    due_at:   Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    escalated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
