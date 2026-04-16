"""Knowledge source management and upload endpoints."""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.knowledge import KnowledgeSource, SourceStatus, SourceType
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeSourceListOut,
    KnowledgeSourceOut,
    ManualKnowledgeCreate,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
settings = get_settings()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "csv", "xlsx", "json"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/json",
}


def _sanitize_filename(filename: str) -> str:
    """Remove path separators and null bytes from filename."""
    name = os.path.basename(filename)
    name = name.replace("\x00", "")
    return name


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


@router.get("", response_model=KnowledgeSourceListOut)
async def list_sources(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    count_result = await db.execute(select(func.count(KnowledgeSource.id)))
    total = count_result.scalar() or 0

    stmt = (
        select(KnowledgeSource)
        .order_by(KnowledgeSource.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    sources = list(result.scalars().all())
    return KnowledgeSourceListOut(sources=sources, total=total)


@router.post("/upload", response_model=KnowledgeSourceOut, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    product_id: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    safe_name = _sanitize_filename(file.filename)
    ext = _get_extension(safe_name)

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: .{ext}. Allowed: {ALLOWED_EXTENSIONS}",
        )

    # Read and check file size
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Store file
    upload_dir = Path(settings.STORAGE_LOCAL_PATH)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}.{ext}"
    file_path.write_bytes(content)

    # Create source record
    source = KnowledgeSource(
        title=title,
        source_type=ext,
        status=SourceStatus.PENDING,
        file_path=str(file_path),
        file_size=len(content),
        original_filename=safe_name,
        product_id=uuid.UUID(product_id) if product_id else None,
        uploaded_by=user.id,
    )
    db.add(source)
    await db.flush()

    audit = AuditService(db)
    await audit.log(
        action="knowledge_uploaded",
        resource_type="knowledge_source",
        resource_id=str(source.id),
        user_id=user.id,
        details={"filename": safe_name, "size": len(content), "type": ext},
    )

    # Trigger async ingestion task via Celery
    from app.tasks.knowledge_tasks import ingest_knowledge_source
    ingest_knowledge_source.delay(str(source.id))

    return source


@router.post("/manual", response_model=KnowledgeSourceOut, status_code=201)
async def create_manual_source(
    body: ManualKnowledgeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    source = KnowledgeSource(
        title=body.title,
        source_type=SourceType.MANUAL,
        status=SourceStatus.PENDING,
        content_text=body.content,
        product_id=body.product_id,
        uploaded_by=user.id,
    )
    db.add(source)
    await db.flush()
    return source


@router.post("/{source_id}/reindex", status_code=202)
async def reindex_source(
    source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    stmt = select(KnowledgeSource).where(KnowledgeSource.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    source.status = SourceStatus.PENDING
    source.version += 1
    await db.flush()

    # Trigger async reindex task via Celery
    from app.tasks.knowledge_tasks import ingest_knowledge_source
    ingest_knowledge_source.delay(str(source_id))

    return {"message": "Reindexing queued", "source_id": str(source_id)}


@router.patch("/{source_id}/toggle")
async def toggle_source(
    source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    stmt = select(KnowledgeSource).where(KnowledgeSource.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    source.is_active = not source.is_active
    await db.flush()
    return {"is_active": source.is_active}
