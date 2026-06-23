"""Background job: promote active orders one stage every 30 seconds.

Orders advance through the lifecycle created → received → processing →
shipped → delivered. Each tick moves every non-terminal order forward by a
single stage. Delivered and cancelled orders are left untouched.
"""
import asyncio

from app.db.database import AsyncSessionLocal
from app.repositories.order_repository import OrderRepository
from app.models.order import next_status

POLL_INTERVAL_SECONDS = 30


async def delivery_transition_loop() -> None:
    print("[delivery_job] Started order promotion job.")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                repo = OrderRepository(db)
                orders = await repo.get_promotable()
                for order in orders:
                    nxt = next_status(order.status)
                    if nxt is None:
                        continue
                    await repo.set_status(order.id, nxt)
                    print(f"[delivery_job] Order {order.order_code} → {nxt.value}")
        except Exception as exc:
            print(f"[delivery_job] Error: {exc}")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
