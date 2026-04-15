"""LLM provider abstraction — OpenAI-compatible interface."""

import time

import openai

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("ai.llm")
settings = get_settings()


class LLMClient:
    """OpenAI-compatible LLM client.

    Supports OpenAI, Azure OpenAI, OpenRouter, and any compatible endpoint.
    """

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self.client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
        )

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """Generate a response from the LLM.

        Returns dict with: response, prompt_tokens, completion_tokens, latency_ms
        """
        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_message})

        start = time.perf_counter()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            latency_ms = int((time.perf_counter() - start) * 1000)
            content = response.choices[0].message.content or ""
            usage = response.usage

            result = {
                "response": content,
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
                "latency_ms": latency_ms,
                "model": self.model,
            }

            logger.info(
                "llm_response_generated",
                model=self.model,
                tokens=result["total_tokens"],
                latency_ms=latency_ms,
            )

            return result

        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            logger.error("llm_error", model=self.model, error=str(e), latency_ms=latency_ms)
            raise
