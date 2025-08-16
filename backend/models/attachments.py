from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from .base import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exception_id: Mapped[int] = mapped_column(ForeignKey("exceptions.id", ondelete="CASCADE"), index=True)

    filename: Mapped[str] = mapped_column(String(255))
    mime: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    s3_key: Mapped[str] = mapped_column(Text)   # path/key in the bucket
    sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
