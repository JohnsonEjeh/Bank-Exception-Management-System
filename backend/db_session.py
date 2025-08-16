from typing import Any, Generator

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import Session
from db import engine

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session() -> Generator[Session, Any, None]:
    with SessionLocal() as session:
        yield session
