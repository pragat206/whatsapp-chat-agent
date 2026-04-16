"""Tests for webhook endpoint and payload parsing."""

import pytest
from httpx import AsyncClient

from app.integrations.aisensy.webhook_handler import parse_webhook_payload


def test_parse_direct_message_payload():
    raw = {
        "event_type": "message",
        "message": {
            "id": "wamid.test123",
            "from_number": "+919876543210",
            "timestamp": "1700000000",
            "type": "text",
            "text": "Hello, I need help",
        },
    }
    payload = parse_webhook_payload(raw)
    assert payload.event_type == "message"
    assert payload.message is not None
    assert payload.message.text == "Hello, I need help"
    assert payload.message.from_number == "+919876543210"


def test_parse_status_payload():
    raw = {
        "event_type": "status",
        "status": {
            "id": "wamid.test456",
            "status": "delivered",
            "timestamp": "1700000001",
            "recipient_id": "+919876543210",
        },
    }
    payload = parse_webhook_payload(raw)
    assert payload.event_type == "status"
    assert payload.status is not None
    assert payload.status.status == "delivered"


def test_parse_whatsapp_cloud_api_format():
    raw = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.cloud123",
                                    "from": "+919876543210",
                                    "timestamp": "1700000002",
                                    "type": "text",
                                    "text": {"body": "Product inquiry"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    payload = parse_webhook_payload(raw)
    assert payload.event_type == "message"
    assert payload.message is not None
    assert payload.message.text == "Product inquiry"


def test_parse_unknown_format():
    raw = {"some_unknown_field": "data"}
    payload = parse_webhook_payload(raw)
    assert payload.event_type == "unknown"
    assert payload.raw_payload == raw


@pytest.mark.asyncio
async def test_webhook_endpoint_accepts_post(client: AsyncClient):
    response = await client.post(
        "/api/v1/webhook/aisensy",
        json={"event_type": "message", "message": {
            "id": "test-1",
            "from_number": "+919876543210",
            "timestamp": "1700000000",
            "type": "text",
            "text": "Hello",
        }},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
