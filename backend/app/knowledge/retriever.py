"""Vector similarity search using pgvector."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.knowledge.embedder import Embedder

logger = get_logger("knowledge.retriever")
settings = get_settings()


class Retriever:
    """Retrieve relevant knowledge chunks using vector similarity search."""

    def __init__(self, db: AsyncSession, embedder: Embedder | None = None):
        self.db = db
        self.embedder = embedder or Embedder()

    async def search(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        product_id: str | None = None,
    ) -> list[dict]:
        """Search for relevant knowledge chunks.

        Returns list of dicts with chunk content, source info, and similarity score.
        """
        query_embedding = await self.embedder.embed_text(query)

        # Build pgvector cosine similarity query
        embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        sql = """
            SELECT
                kc.id as chunk_id,
                kc.content,
                kc.chunk_index,
                ks.title as source_title,
                ks.source_type,
                ks.product_id,
                1 - (er.embedding <=> :embedding::vector) as similarity
            FROM embedding_records er
            JOIN knowledge_chunks kc ON kc.id = er.chunk_id
            JOIN knowledge_sources ks ON ks.id = kc.source_id
            WHERE ks.is_active = true
                AND ks.status = 'indexed'
        """

        if product_id:
            sql += " AND ks.product_id = :product_id"

        sql += """
            ORDER BY er.embedding <=> :embedding::vector
            LIMIT :top_k
        """

        params: dict = {
            "embedding": embedding_str,
            "top_k": top_k,
        }
        if product_id:
            params["product_id"] = product_id

        result = await self.db.execute(text(sql), params)
        rows = result.fetchall()

        chunks = []
        for row in rows:
            similarity = float(row.similarity) if row.similarity else 0.0
            if similarity >= similarity_threshold:
                chunks.append({
                    "chunk_id": str(row.chunk_id),
                    "content": row.content,
                    "chunk_index": row.chunk_index,
                    "source_title": row.source_title,
                    "source_type": row.source_type,
                    "product_id": str(row.product_id) if row.product_id else None,
                    "similarity": round(similarity, 4),
                })

        logger.info(
            "retrieval_complete",
            query_length=len(query),
            results=len(chunks),
            top_similarity=chunks[0]["similarity"] if chunks else 0.0,
        )

        return chunks
