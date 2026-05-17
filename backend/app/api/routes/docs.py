import io
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.models.document import Document
from app.schemas.doc import DocumentOut
from app.services.rag import get_rag_store

router = APIRouter()
logger = logging.getLogger(__name__)


def extract_text(file: UploadFile, data: bytes) -> str:
    if file.content_type == "application/pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PDF support is not installed.",
            ) from exc
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if file.content_type and file.content_type.startswith("text/"):
        return data.decode("utf-8", errors="ignore")
    if file.content_type in {None, "application/octet-stream"}:
        return data.decode("utf-8", errors="ignore")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")


@router.post("/upload", response_model=DocumentOut)
async def upload_doc(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> DocumentOut:
    try:
        data = await file.read()
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

        text = extract_text(file, data)
        rag = get_rag_store()
        document = await rag.add_document(
            db,
            user_id=user.id,
            filename=file.filename or "document",
            content=text,
            content_type=file.content_type,
            source="upload",
        )

        db.add(AuditLog(user_id=user.id, event_type="doc_upload", detail=file.filename))
        await db.commit()
        return document
    except HTTPException:
        raise
    except ImportError as exc:
        logger.exception("Upload dependency import failure")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload dependency missing: {exc}",
        ) from exc
    except SQLAlchemyError as exc:
        logger.exception("Database failure while uploading document")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while storing document.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected upload failure")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {type(exc).__name__}: {exc}",
        ) from exc


@router.get("/", response_model=list[DocumentOut])
async def list_docs(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> list[DocumentOut]:
    result = await db.execute(select(Document).where(Document.user_id == user.id))
    return list(result.scalars().all())


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doc(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    try:
        result = await db.execute(
            select(Document).where(Document.id == document_id, Document.user_id == user.id)
        )
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        filename = document.filename
        rag = get_rag_store()
        rag.delete_document(user.id, document.id)
        await db.delete(document)

        db.add(AuditLog(user_id=user.id, event_type="doc_deleted", detail=filename))
        await db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Document delete failed")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document delete failed: {type(exc).__name__}: {exc}",
        ) from exc
