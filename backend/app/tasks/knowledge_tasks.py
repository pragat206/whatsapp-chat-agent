"""Background tasks for knowledge ingestion."""

import asyncio
import uuid

from app.core.database import async_session_factory
from app.core.logging import get_logger
from app.knowledge.ingestion import IngestionPipeline
from app.tasks.celery_app import celery_app

logger = get_logger("tasks.knowledge")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_knowledge_source(self, source_id: str):
    """Async task to ingest a knowledge source."""

    async def _run():
        async with async_session_factory() as session:
            try:
                pipeline = IngestionPipeline(session)

                # Read file bytes if file-based
                from sqlalchemy import select
                from app.models.knowledge import KnowledgeSource

                stmt = select(KnowledgeSource).where(
                    KnowledgeSource.id == uuid.UUID(source_id)
                )
                result = await session.execute(stmt)
                source = result.scalar_one_or_none()

                if not source:
                    logger.error("task_source_not_found", source_id=source_id)
                    return

                file_bytes = None
                if source.file_path:
                    from pathlib import Path

                    path = Path(source.file_path)
                    if path.exists():
                        file_bytes = path.read_bytes()

                success = await pipeline.ingest_source(
                    uuid.UUID(source_id), file_bytes
                )
                await session.commit()

                if success:
                    logger.info("task_ingestion_complete", source_id=source_id)
                else:
                    logger.error("task_ingestion_failed", source_id=source_id)

            except Exception as e:
                await session.rollback()
                logger.error("task_ingestion_error", source_id=source_id, error=str(e))
                raise self.retry(exc=e)

    asyncio.run(_run())


@celery_app.task
def reindex_all_sources():
    """Reindex all active knowledge sources."""

    async def _run():
        async with async_session_factory() as session:
            from sqlalchemy import select
            from app.models.knowledge import KnowledgeSource, SourceStatus

            stmt = select(KnowledgeSource).where(
                KnowledgeSource.is_active.is_(True),
                KnowledgeSource.status == SourceStatus.INDEXED,
            )
            result = await session.execute(stmt)
            sources = result.scalars().all()

            for source in sources:
                ingest_knowledge_source.delay(str(source.id))

            logger.info("reindex_queued", count=len(sources))

    asyncio.run(_run())
