from typing import Optional
from pydantic import BaseModel

class PresignUploadIn(BaseModel):
    exception_id: int
    filename: str
    mime: Optional[str] = None
    uploaded_by: Optional[int] = None

class PresignUploadOut(BaseModel):
    attachment_id: int
    upload_url: str
    key: str

class PresignDownloadIn(BaseModel):
    attachment_id: int

class PresignDownloadOut(BaseModel):
    download_url: str
