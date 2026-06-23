from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_user_optional
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.schemas.chat import ChatRequest
from app.agent.agent import stream_agent_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(
    body: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    # Guests (no valid token) can use the agent for policy questions only.
    order_repo = OrderRepository(db) if current_user else None
    user_id = current_user.id if current_user else None

    async def generator():
        async for chunk in stream_agent_response(
            user_id=user_id,
            order_repo=order_repo,
            messages=[m.model_dump() for m in body.messages],
        ):
            yield chunk

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
