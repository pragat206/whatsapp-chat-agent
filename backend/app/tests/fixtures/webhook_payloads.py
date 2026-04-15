"""Sample webhook payloads for local testing."""

# Direct AiSensy format (estimated)
AISENSY_INBOUND_TEXT = {
    "event_type": "message",
    "message": {
        "id": "wamid.HBgNOTE4NzY1NDMyMTAVAgASGCA2Mjg4NDUxRTc2RTk0OTY2MEU5MjdCQjk5RTg5RDMYAA==",
        "from_number": "+919876543210",
        "timestamp": "1700000000",
        "type": "text",
        "text": "Hi, I want to know about your products",
    },
    "contact": {
        "wa_id": "919876543210",
        "profile_name": "Rahul Kumar",
    },
}

AISENSY_INBOUND_IMAGE = {
    "event_type": "message",
    "message": {
        "id": "wamid.image123",
        "from_number": "+919876543210",
        "timestamp": "1700000001",
        "type": "image",
        "text": None,
        "media_url": "https://example.com/image.jpg",
        "caption": "Check this product",
    },
}

AISENSY_STATUS_DELIVERED = {
    "event_type": "status",
    "status": {
        "id": "wamid.outbound001",
        "status": "delivered",
        "timestamp": "1700000002",
        "recipient_id": "+919876543210",
    },
}

AISENSY_STATUS_READ = {
    "event_type": "status",
    "status": {
        "id": "wamid.outbound001",
        "status": "read",
        "timestamp": "1700000003",
        "recipient_id": "+919876543210",
    },
}

AISENSY_STATUS_FAILED = {
    "event_type": "status",
    "status": {
        "id": "wamid.outbound002",
        "status": "failed",
        "timestamp": "1700000004",
        "recipient_id": "+919876543210",
        "errors": [{"code": 131047, "title": "Message expired"}],
    },
}

# WhatsApp Cloud API format (for reference/compatibility)
CLOUD_API_INBOUND = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "BIZ_ACCOUNT_ID",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15551234567",
                            "phone_number_id": "PHONE_NUMBER_ID",
                        },
                        "contacts": [
                            {
                                "profile": {"name": "Priya Sharma"},
                                "wa_id": "919876543211",
                            }
                        ],
                        "messages": [
                            {
                                "from": "919876543211",
                                "id": "wamid.cloudmsg001",
                                "timestamp": "1700000005",
                                "type": "text",
                                "text": {"body": "What is the price of SmartHome Hub?"},
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

CLOUD_API_STATUS = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "BIZ_ACCOUNT_ID",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "statuses": [
                            {
                                "id": "wamid.outbound003",
                                "status": "sent",
                                "timestamp": "1700000006",
                                "recipient_id": "919876543211",
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}
