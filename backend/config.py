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

    # S3 / MinIO
    s3_endpoint: str = _clean(os.getenv("S3_ENDPOINT"), "http://127.0.0.1:9000")
    s3_region: str = _clean(os.getenv("S3_REGION"), "us-east-1")
    s3_access_key: str = _clean(os.getenv("S3_ACCESS_KEY"), "admin")
    s3_secret_key: str = _clean(os.getenv("S3_SECRET_KEY"), "adminadmin")
    s3_bucket: str = _clean(os.getenv("S3_BUCKET"), "ems-attachments")
    s3_secure: bool = os.getenv("S3_SECURE", "false").lower() == "true"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
