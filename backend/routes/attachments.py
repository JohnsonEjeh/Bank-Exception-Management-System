import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db_session import get_session
from storage.s3 import ensure_bucket, presign_put, presign_get
from schemas.attachment import PresignUploadIn, PresignUploadOut, PresignDownloadIn, PresignDownloadOut
from models.attachment import Attachment
from models.exception import Exception as ExceptionModel

router = APIRouter(prefix="/attachments", tags=["attachments"])

@router.post("/presign-upload", response_model=PresignUploadOut)
def presign_upload(payload: PresignUploadIn, db: Session = Depends(get_session)):
    # validate exception exists
    exc = db.get(ExceptionModel, payload.exception_id)
    if not exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exception not found")

    ensure_bucket()
    # key pattern: exceptions/{id}/{uuid}_{filename}
    safe_name = payload.filename.replace("\\", "/").split("/")[-1]
    key = f"exceptions/{payload.exception_id}/{uuid.uuid4().hex}_{safe_name}"

    url = presign_put(key, payload.mime, expires_seconds=600)

    # create DB record now (simple flow). Optional: add a later "finalize" endpoint to verify upload.
    att = Attachment(
        exception_id=payload.exception_id,
        filename=safe_name,
        mime=payload.mime,
        s3_key=key,
        uploaded_by=payload.uploaded_by,
    )
    db.add(att)
    db.commit()
    db.refresh(att)

    return PresignUploadOut(attachment_id=att.id, upload_url=url, key=key)

@router.post("/presign-download", response_model=PresignDownloadOut)
def presign_download(payload: PresignDownloadIn, db: Session = Depends(get_session)):
    att = db.get(Attachment, payload.attachment_id)
    if not att:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    url = presign_get(att.s3_key, expires_seconds=600)
    return PresignDownloadOut(download_url=url)

@router.get("/by-exception/{exc_id}", response_model=List[dict])
def list_for_exception(exc_id: int, db: Session = Depends(get_session)):
    rows = (
        db.query(Attachment)
        .filter(Attachment.exception_id == exc_id)
        .order_by(Attachment.id.desc())
        .all()
    )
    # quick dicts (avoid writing a separate Out schema for brevity)
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "mime": r.mime,
            "uploaded_by": r.uploaded_by,
            "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
        }
        for r in rows
    ]
