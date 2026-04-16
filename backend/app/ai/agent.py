"""WhatsApp AI agent — orchestrates RAG, LLM, and conversation logic."""

import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm_client import LLMClient
from app.ai.prompts import (
    CONFIDENCE_CHECK_PROMPT,
    FALLBACK_MESSAGE,
    HANDOFF_POLICY,
    LEAD_QUALIFICATION_PROMPT,
    SYSTEM_PROMPT_TEMPLATE,
)
from app.core.logging import get_logger
from app.knowledge.retriever import Retriever
from app.models.ai_run import AIRun
from app.models.conversation import Conversation, Message, MessageDirection

logger = get_logger("ai.agent")


class WhatsAppAIAgent:
    """Core AI agent that handles inbound messages and generates responses."""

    def __init__(
        self,
        db: AsyncSession,
        business_name: str = "Our Business",
        tone: str = "professional and friendly",
        additional_instructions: str = "",
    ):
        self.db = db
        self.llm = LLMClient()
        self.retriever = Retriever(db)
        self.business_name = business_name
        self.tone = tone
        self.additional_instructions = additional_instructions

    async def process_message(
        self,
        conversation: Conversation,
        user_message: str,
    ) -> dict:
        """Process an inbound message and generate an AI response.

        Returns dict with:
        - response: str — the AI reply text
        - confidence: float — confidence score
        - should_handoff: bool — whether to escalate
        - lead_data: dict | None — extracted lead info
        - ai_run_id: UUID — tracking ID
        - retrieved_chunks: list — source chunks used
        """
        # Check for handoff triggers in user message
        if self._check_handoff_triggers(user_message):
            return {
                "response": "I understand you'd like to speak with our team directly. Let me connect you with a human agent who can assist you better. Please hold on!",
                "confidence": 1.0,
                "should_handoff": True,
                "lead_data": None,
                "ai_run_id": None,
                "retrieved_chunks": [],
            }

        # Step 1: Retrieve relevant knowledge
        retrieved_chunks = await self.retriever.search(
            query=user_message,
            top_k=5,
            similarity_threshold=0.65,
        )

        knowledge_context = self._format_knowledge_context(retrieved_chunks)

        # Step 2: Build conversation history
        history = await self._get_conversation_history(conversation)

        # Step 3: Build system prompt
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            business_name=self.business_name,
            tone=self.tone,
            additional_instructions=self.additional_instructions,
            knowledge_context=knowledge_context or "No specific knowledge available for this query.",
        )

        # Step 4: Generate response
        llm_result = await self.llm.generate(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=history,
        )

        response_text = llm_result["response"]

        # Step 5: Assess confidence
        confidence = await self._assess_confidence(
            user_message, response_text, knowledge_context
        )

        # Step 6: Handle low confidence
        should_handoff = False
        if confidence < HANDOFF_POLICY["confidence_threshold"]:
            logger.warning(
                "low_confidence_response",
                confidence=confidence,
                conversation_id=str(conversation.id),
            )
            if confidence < 0.4:
                response_text = FALLBACK_MESSAGE
                should_handoff = True
            else:
                response_text += "\n\nIf you need more specific details, I can connect you with our team. Just let me know!"

        # Step 7: Log AI run
        ai_run = AIRun(
            conversation_id=conversation.id,
            model_name=llm_result["model"],
            prompt_tokens=llm_result["prompt_tokens"],
            completion_tokens=llm_result["completion_tokens"],
            total_tokens=llm_result["total_tokens"],
            latency_ms=llm_result["latency_ms"],
            system_prompt=system_prompt[:5000],
            user_input=user_message[:2000],
            ai_output=response_text[:5000],
            confidence_score=confidence,
            retrieved_chunks=[
                {"chunk_id": c["chunk_id"], "source": c["source_title"], "similarity": c["similarity"]}
                for c in retrieved_chunks
            ],
        )
        self.db.add(ai_run)
        await self.db.flush()

        # Step 8: Extract lead data (non-blocking, best effort)
        lead_data = None
        try:
            lead_data = await self._extract_lead_data(conversation, user_message)
        except Exception as e:
            logger.warning("lead_extraction_failed", error=str(e))

        return {
            "response": response_text,
            "confidence": confidence,
            "should_handoff": should_handoff,
            "lead_data": lead_data,
            "ai_run_id": ai_run.id,
            "retrieved_chunks": retrieved_chunks,
        }

    def _check_handoff_triggers(self, message: str) -> bool:
        """Check if message contains handoff trigger phrases."""
        lower = message.lower()
        return any(trigger in lower for trigger in HANDOFF_POLICY["triggers"])

    def _format_knowledge_context(self, chunks: list[dict]) -> str:
        """Format retrieved chunks into context string."""
        if not chunks:
            return ""

        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[Source {i}: {chunk['source_title']}]\n{chunk['content']}"
            )
        return "\n\n---\n\n".join(parts)

    async def _get_conversation_history(
        self, conversation: Conversation, max_messages: int = 10
    ) -> list[dict]:
        """Get recent conversation history formatted for LLM."""
        from sqlalchemy import select

        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(max_messages)
        )
        result = await self.db.execute(stmt)
        messages = list(reversed(result.scalars().all()))

        history = []
        for msg in messages:
            role = "user" if msg.direction == MessageDirection.INBOUND else "assistant"
            history.append({"role": role, "content": msg.content})

        return history

    async def _assess_confidence(
        self, question: str, response: str, context: str
    ) -> float:
        """Use LLM to assess response confidence."""
        try:
            prompt = CONFIDENCE_CHECK_PROMPT.format(
                question=question[:500],
                response=response[:500],
                context_summary=context[:1000] if context else "No context available",
            )
            result = await self.llm.generate(
                system_prompt="You are a confidence assessor. Respond with ONLY a number between 0.0 and 1.0.",
                user_message=prompt,
            )
            score = float(result["response"].strip())
            return max(0.0, min(1.0, score))
        except (ValueError, Exception):
            # Default to moderate confidence if assessment fails
            return 0.7 if context else 0.4

    async def _extract_lead_data(
        self, conversation: Conversation, latest_message: str
    ) -> dict | None:
        """Extract lead qualification data from conversation."""
        history = await self._get_conversation_history(conversation, max_messages=20)
        history_text = "\n".join(
            f"{'Customer' if m['role'] == 'user' else 'Agent'}: {m['content']}"
            for m in history
        )
        history_text += f"\nCustomer: {latest_message}"

        prompt = LEAD_QUALIFICATION_PROMPT.format(conversation_history=history_text)

        result = await self.llm.generate(
            system_prompt="You are a lead data extractor. Respond with ONLY valid JSON.",
            user_message=prompt,
        )

        try:
            data = json.loads(result["response"])
            # Filter out null/None values
            return {k: v for k, v in data.items() if v is not None} or None
        except json.JSONDecodeError:
            return None
