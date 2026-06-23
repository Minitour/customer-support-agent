from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_user_optional
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.chat import ChatRequest, ChatContext
from app.agent.agent import stream_agent_response

router = APIRouter(prefix="/chat", tags=["chat"])


async def _build_context_text(
    product_repo: ProductRepository, context: ChatContext | None
) -> str | None:
    """Resolve the product IDs from the client context into product names and
    format them as a prompt block the agent can reason about."""
    if context is None:
        return None

    on_screen_ids = context.products_on_screen or []
    cart_ids = context.products_in_cart or []
    if not on_screen_ids and not cart_ids:
        return None

    products = await product_repo.get_by_ids(list({*on_screen_ids, *cart_ids}))
    by_id = {p.id: p for p in products}

    def _format(ids: list[int]) -> list[str]:
        formatted = []
        for pid in ids:
            p = by_id.get(pid)
            if p is not None:
                formatted.append(f"- {p.title} (ID: {p.id})")
        return formatted

    lines = [
        "## Current page context",
        "Use this to understand what the customer is referring to when they say "
        '"this", "these", "the item on my screen", "my cart", etc. '
        "Call `get_products_by_id` with the relevant IDs if you need fuller details.",
    ]

    screen = _format(on_screen_ids)
    if screen:
        lines.append("\nProducts currently on the customer's screen:")
        lines.extend(screen)
    else:
        lines.append("\nThe customer is not viewing any specific products right now.")

    cart = _format(cart_ids)
    if cart:
        lines.append("\nProducts currently in the customer's cart:")
        lines.extend(cart)
    else:
        lines.append("\nThe customer's cart is empty.")

    return "\n".join(lines)


@router.post("/stream")
async def chat_stream(
    body: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    # Guests (no valid token) can use the agent for policy questions only.
    order_repo = OrderRepository(db) if current_user else None
    user_id = current_user.id if current_user else None
    product_repo = ProductRepository(db)

    context_text = await _build_context_text(product_repo, body.context)

    async def generator():
        async for chunk in stream_agent_response(
            user_id=user_id,
            order_repo=order_repo,
            product_repo=product_repo,
            messages=[m.model_dump() for m in body.messages],
            context_text=context_text,
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
