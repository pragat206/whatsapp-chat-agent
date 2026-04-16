"""Knowledge ingestion pipeline: parse → chunk → embed → store."""

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.knowledge.chunker import chunk_text
from app.knowledge.embedder import Embedder
from app.knowledge.parser import parse_file
from app.models.knowledge import KnowledgeChunk, KnowledgeSource, SourceStatus

logger = get_logger("knowledge.ingestion")


class IngestionPipeline:
    """Full pipeline: parse file → chunk text → generate embeddings → store in pgvector."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedder = Embedder()

    async def ingest_source(self, source_id: uuid.UUID, file_bytes: bytes | None = None) -> bool:
        """Process a knowledge source end-to-end.

        Returns True on success, False on failure.
        """
        from sqlalchemy import select

        stmt = select(KnowledgeSource).where(KnowledgeSource.id == source_id)
        result = await self.db.execute(stmt)
        source = result.scalar_one_or_none()

        if not source:
            logger.error("ingestion_source_not_found", source_id=str(source_id))
            return False

        try:
            source.status = SourceStatus.PROCESSING
            await self.db.flush()

            # Step 1: Parse content
            if file_bytes:
                content = parse_file(file_bytes, source.source_type)
            elif source.content_text:
                content = source.content_text
            else:
                raise ValueError("No content available for ingestion")

            if not content.strip():
                raise ValueError("Parsed content is empty")

            source.content_text = content

            # Step 2: Chunk
            chunks = chunk_text(content, chunk_size=500, chunk_overlap=50)
            logger.info("chunking_complete", source_id=str(source_id), chunks=len(chunks))

            # Step 3: Delete old chunks if re-indexing
            await self.db.execute(
                text("DELETE FROM embedding_records WHERE chunk_id IN "
                     "(SELECT id FROM knowledge_chunks WHERE source_id = :sid)"),
                {"sid": source_id},
            )
            await self.db.execute(
                text("DELETE FROM knowledge_chunks WHERE source_id = :sid"),
                {"sid": source_id},
            )

            # Step 4: Create chunks
            chunk_records = []
            for i, chunk_content in enumerate(chunks):
                chunk = KnowledgeChunk(
                    source_id=source_id,
                    chunk_index=i,
                    content=chunk_content,
                    token_count=len(chunk_content.split()),
                )
                self.db.add(chunk)
                chunk_records.append(chunk)

            await self.db.flush()

            # Step 5: Generate and store embeddings
            texts = [c.content for c in chunk_records]
            embeddings = await self.embedder.embed_batch(texts)

            for chunk_record, embedding in zip(chunk_records, embeddings):
                embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"
                await self.db.execute(
                    text("""
                        INSERT INTO embedding_records (id, chunk_id, model_name, dimensions, embedding, created_at, updated_at)
                        VALUES (gen_random_uuid(), :chunk_id, :model, :dims, :embedding::vector, now(), now())
                    """),
                    {
                        "chunk_id": chunk_record.id,
                        "model": self.embedder.model,
                        "dims": self.embedder.dimensions,
                        "embedding": embedding_str,
                    },
                )

            # Update source status
            source.status = SourceStatus.INDEXED
            source.chunk_count = len(chunks)
            source.error_message = None
            await self.db.flush()

            logger.info(
                "ingestion_complete",
                source_id=str(source_id),
                chunks=len(chunks),
            )
            return True

        except Exception as e:
            source.status = SourceStatus.FAILED
            source.error_message = str(e)[:2000]
            await self.db.flush()
            logger.error("ingestion_failed", source_id=str(source_id), error=str(e))
            return False
