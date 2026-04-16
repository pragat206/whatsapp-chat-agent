"""Conversation management API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_operator
from app.integrations.aisensy.client import get_bsp_provider
from app.models.user import User
from app.schemas.conversation import (
    ConversationDetail,
    ConversationListOut,
    ConversationUpdate,
    HandoffRequest,
    NoteCreate,
    NoteOut,
    SendMessageRequest,
)
from app.services.audit_service import AuditService
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationListOut)
async def list_conversations(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = ConversationService(db)
    conversations, total = await service.list_conversations(
        status=status, limit=limit, offset=offset
    )
    return ConversationListOut(conversations=conversations, total=total)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = ConversationService(db)
    conv = await service.get_conversation_detail(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.patch("/{conversation_id}", response_model=ConversationDetail)
async def update_conversation(
    conversation_id: uuid.UUID,
    body: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_operator),
):
    service = ConversationService(db)
    updates = body.model_dump(exclude_none=True)
    conv = await service.update_conversation(conversation_id, **updates)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    audit = AuditService(db)
    await audit.log(
        action="conversation_updated",
        resource_type="conversation",
        resource_id=str(conversation_id),
        user_id=user.id,
        details=updates,
    )

    return await service.get_conversation_detail(conversation_id)


@router.post("/{conversation_id}/handoff")
async def initiate_handoff(
    conversation_id: uuid.UUID,
    body: HandoffRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_operator),
):
    service = ConversationService(db)
    event = await service.initiate_handoff(
        conversation_id=conversation_id,
        user_id=user.id,
        reason=body.reason,
    )
    return {"message": "Handoff initiated", "event_id": str(event.id)}


@router.post("/{conversation_id}/resume-ai")
async def resume_ai(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_operator),
):
    service = ConversationService(db)
    conv = await service.resume_ai(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "AI mode resumed"}


@router.post("/{conversation_id}/notes", response_model=NoteOut)
async def add_note(
    conversation_id: uuid.UUID,
    body: NoteCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_operator),
):
    service = ConversationService(db)
    note = await service.add_note(
        conversation_id=conversation_id,
        author_id=user.id,
        content=body.content,
    )
    return note


@router.post("/{conversation_id}/send")
async def send_reply(
    conversation_id: uuid.UUID,
    body: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_operator),
):
    """Manually send a reply to a conversation (human agent reply)."""
    service = ConversationService(db)
    conv = await service.get_conversation_detail(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Send via BSP
    bsp = get_bsp_provider()
    try:
        result = await bsp.send_message(
            to=conv.contact.phone_number,
            message=body.content,
        )
        external_id = result.get("id")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to send message: {str(e)}")

    # Store outbound message
    msg = await service.store_outbound_message(
        conversation=conv,
        content=body.content,
        is_ai_generated=False,
        external_id=external_id,
    )

    return {"message": "Reply sent", "message_id": str(msg.id)}
