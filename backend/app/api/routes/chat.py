import asyncio
import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db, AsyncSessionLocal
from app.api.dependencies import get_current_user_optional
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ChatRequest, ChatContext, ConversationMessagesResponse, MessageOut
from app.agent.agent import stream_agent_response

router = APIRouter(prefix="/chat", tags=["chat"])

# Keep strong references to in-flight background generations so they are not
# garbage collected if the client disconnects before the agent finishes.
_background_tasks: set[asyncio.Task] = set()


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
    user_id = current_user.id if current_user else None
    conv_repo = ConversationRepository(db)
    user_repo = UserRepository(db) if current_user else None
    product_repo = ProductRepository(db)

    # Resolve or create conversation
    if body.conversation_id is not None:
        conversation = await conv_repo.get_owned(body.conversation_id, user_id)
    else:
        conversation = await conv_repo.create(user_id)

    conversation_id: uuid.UUID = conversation.id

    # Persist the incoming user message
    await conv_repo.add_message(conversation_id, "user", body.message)

    # Load full history from DB (includes the message we just saved)
    db_messages = await conv_repo.list_messages(conversation_id)
    history = [{"role": m.role, "content": m.content} for m in db_messages]

    # Resolve page context now (uses the request-scoped session, which is fine
    # because this completes before we hand off to the background task).
    context_text = await _build_context_text(product_repo, body.context)

    # The agent generation runs in a background task with its OWN database
    # session so it survives client disconnects. The streaming response merely
    # relays events from a queue; if the client goes away, the background task
    # keeps running to completion and persists the assistant reply.
    queue: asyncio.Queue = asyncio.Queue()

    async def run_agent():
        assistant_content_parts: list[str] = []
        try:
            async with AsyncSessionLocal() as bg_db:
                bg_order_repo = OrderRepository(bg_db) if user_id is not None else None
                bg_product_repo = ProductRepository(bg_db)
                bg_conv_repo = ConversationRepository(bg_db)

                async for chunk in stream_agent_response(
                    user_id=user_id,
                    order_repo=bg_order_repo,
                    product_repo=bg_product_repo,
                    messages=history,
                    context_text=context_text,
                    user_repo=user_repo
                ):
                    if chunk.startswith("data: "):
                        try:
                            event = json.loads(chunk[6:])
                            if event.get("type") == "token" and event.get("content"):
                                assistant_content_parts.append(event["content"])
                        except Exception:
                            pass
                    await queue.put(chunk)

                # Persist the completed assistant reply regardless of whether the
                # client is still connected.
                full_content = "".join(assistant_content_parts)
                if full_content:
                    await bg_conv_repo.add_message(conversation_id, "assistant", full_content)
        except Exception as exc:  # noqa: BLE001
            # Persist whatever was generated before the failure, then surface error.
            partial = "".join(assistant_content_parts)
            if partial:
                try:
                    async with AsyncSessionLocal() as err_db:
                        await ConversationRepository(err_db).add_message(
                            conversation_id, "assistant", partial
                        )
                except Exception:
                    pass
            await queue.put(
                f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
            )
        finally:
            await queue.put(None)  # sentinel: generation finished

    task = asyncio.create_task(run_agent())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    async def generator():
        # Emit conversation id as first event so the client can store it
        yield f"data: {json.dumps({'type': 'conversation', 'conversation_id': str(conversation_id)})}\n\n"

        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationMessagesResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id if current_user else None
    conv_repo = ConversationRepository(db)

    conversation = await conv_repo.get_owned(conversation_id, user_id)
    db_messages = await conv_repo.list_messages(conversation.id)

    return ConversationMessagesResponse(
        conversation_id=conversation.id,
        messages=[
            MessageOut(role=m.role, content=m.content, created_at=m.created_at)
            for m in db_messages
        ],
    )
