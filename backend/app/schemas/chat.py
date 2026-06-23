from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatContext(BaseModel):
    """Client-supplied context describing what the customer is currently seeing.

    Only product IDs are sent from the frontend; the backend resolves them to
    product names before injecting them into the agent's prompt.
    """

    products_on_screen: List[int] = Field(default_factory=list)
    products_in_cart: List[int] = Field(default_factory=list)


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[ChatContext] = None
