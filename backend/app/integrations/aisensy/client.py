"""AiSensy API client — BSP integration adapter.

This module provides a clean abstraction over the AiSensy messaging API.
All provider-specific field mappings are contained here so that swapping
to a different BSP only requires implementing the same interface.

TODO: Confirm exact API endpoints and payload formats from AiSensy documentation.
The current implementation is based on standard WhatsApp Business API patterns
and AiSensy's known API structure.
"""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("aisensy")
settings = get_settings()


class AiSensyClient:
    """HTTP client for AiSensy API interactions."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        project_id: str | None = None,
    ):
        self.api_key = api_key or settings.AISENSY_API_KEY
        self.base_url = (base_url or settings.AISENSY_API_BASE_URL).rstrip("/")
        self.project_id = project_id or settings.AISENSY_PROJECT_ID

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def send_text_message(self, to: str, message: str) -> dict:
        """Send a text message via AiSensy.

        TODO: Confirm exact endpoint path and payload format.
        AiSensy may use /campaign/send or /message/send depending on plan.
        """
        payload = {
            "apiKey": self.api_key,
            "campaignName": "whatsapp_agent_reply",
            "destination": to,
            "userName": "AI Agent",
            "source": "ai-agent-platform",
            "message": message,
            # TODO: Confirm if templateParams or other fields are needed
            # for session messages vs template messages
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/direct/send",
                json=payload,
                headers=self._headers(),
            )

            if response.status_code >= 400:
                logger.error(
                    "aisensy_send_failed",
                    status=response.status_code,
                    body=response.text[:500],
                    to=to[:6] + "****",
                )
                response.raise_for_status()

            result = response.json()
            logger.info("aisensy_message_sent", to=to[:6] + "****", message_id=result.get("id"))
            return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        template_params: list[str] | None = None,
    ) -> dict:
        """Send a template message via AiSensy.

        TODO: Confirm exact template message API format.
        """
        payload = {
            "apiKey": self.api_key,
            "campaignName": template_name,
            "destination": to,
            "userName": "AI Agent",
            "templateParams": template_params or [],
            "source": "ai-agent-platform",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/campaign/send",
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()


class BSPProvider:
    """Abstract BSP interface for provider swapping."""

    async def send_message(self, to: str, message: str) -> dict:
        raise NotImplementedError

    async def send_template(
        self, to: str, template: str, params: list[str] | None = None
    ) -> dict:
        raise NotImplementedError


class AiSensyProvider(BSPProvider):
    """AiSensy implementation of BSP provider interface."""

    def __init__(self):
        self.client = AiSensyClient()

    async def send_message(self, to: str, message: str) -> dict:
        return await self.client.send_text_message(to, message)

    async def send_template(
        self, to: str, template: str, params: list[str] | None = None
    ) -> dict:
        return await self.client.send_template_message(to, template, params)


def get_bsp_provider() -> BSPProvider:
    """Factory function to get the configured BSP provider."""
    return AiSensyProvider()
