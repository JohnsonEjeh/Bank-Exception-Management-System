from __future__ import annotations

from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os

# Always load .env from the repo root (../.env relative to this file)
ROOT_ENV = Path(__file__).resolve().parents[1].parent / ".env"
if ROOT_ENV.exists():
    load_dotenv(ROOT_ENV)

def _clean(val: str, default: str) -> str:
    if not val:
        return default
    if val.strip().lower() in ("none", "null", "nil", ""):
        return default
    return val

class Settings(BaseModel):
    db_user: str = _clean(os.getenv("PGUSER"), "postgres")
    db_password: str = _clean(os.getenv("PGPASSWORD"), "password")
    db_host: str = _clean(os.getenv("PGHOST"), "127.0.0.1")
    db_port: str = _clean(os.getenv("PGPORT"), "5433")
    db_name: str = _clean(os.getenv("PGDATABASE"), "ems")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
