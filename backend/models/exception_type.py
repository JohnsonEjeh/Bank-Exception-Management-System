from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Integer, Text
from .base import Base, TimestampMixin

class ExceptionType(Base, TimestampMixin):
    __tablename__ = "exception_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    default_sla_hours: Mapped[int] = mapped_column(Integer, default=72, server_default="72")
    approval_levels:   Mapped[int] = mapped_column(Integer, default=1,  server_default="1")
    active:            Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
