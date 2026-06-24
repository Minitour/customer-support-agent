import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatContext(BaseModel):
    """Client-supplied context describing what the customer is currently seeing.

    Only product IDs are sent from the frontend; the backend resolves them to
    product names before injecting them into the agent's prompt.
    """

    products_on_screen: List[int] = Field(default_factory=list)
    products_in_cart: List[int] = Field(default_factory=list)


class ChatRequest(BaseModel):
    conversation_id: Optional[uuid.UUID] = None
    message: str
    context: Optional[ChatContext] = None


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationMessagesResponse(BaseModel):
    conversation_id: uuid.UUID
    messages: List[MessageOut]
