import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, ConversationMessage


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: Optional[int]) -> Conversation:
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_owned(
        self, conversation_id: uuid.UUID, user_id: Optional[int]
    ) -> Conversation:
        """Return the conversation, enforcing ownership.

        - user_id=None (guest): may only access conversations where user_id IS NULL.
        - user_id=N (authenticated): may only access conversations where user_id = N.
        Raises 404 if not found, 403 if found but not owned.
        """
        conversation = await self.get(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        if conversation.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return conversation

    async def add_message(
        self, conversation_id: uuid.UUID, role: str, content: str
    ) -> ConversationMessage:
        msg = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.db.add(msg)
        # Bump updated_at on the parent conversation
        await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = await self.get(conversation_id)
        if conv is not None:
            conv.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def list_messages(self, conversation_id: uuid.UUID) -> list[ConversationMessage]:
        result = await self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at, ConversationMessage.id)
        )
        return list(result.scalars().all())
