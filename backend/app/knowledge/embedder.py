"""Embedding generation using OpenAI-compatible API."""

import openai

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("knowledge.embedder")
settings = get_settings()


class Embedder:
    """Generate embeddings using OpenAI-compatible API."""

    def __init__(self, model: str | None = None, dimensions: int | None = None):
        self.model = model or settings.EMBEDDING_MODEL
        self.dimensions = dimensions or settings.EMBEDDING_DIMENSIONS
        self.client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
        )

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """Generate embeddings for multiple texts in batches."""
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = await self.client.embeddings.create(
                model=self.model,
                input=batch,
            )
            batch_embeddings = [d.embedding for d in response.data]
            all_embeddings.extend(batch_embeddings)
            logger.info(
                "embeddings_generated",
                batch=i // batch_size + 1,
                count=len(batch),
            )

        return all_embeddings
