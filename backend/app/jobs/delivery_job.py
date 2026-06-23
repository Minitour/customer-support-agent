"""Background job: transition placed orders older than 30s to out_for_delivery."""
import asyncio

from app.db.database import AsyncSessionLocal
from app.repositories.order_repository import OrderRepository
from app.models.order import OrderStatus

POLL_INTERVAL_SECONDS = 10
ORDER_AGE_THRESHOLD_SECONDS = 30


async def delivery_transition_loop() -> None:
    print("[delivery_job] Started auto-delivery transition job.")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                repo = OrderRepository(db)
                orders = await repo.get_placed_older_than(ORDER_AGE_THRESHOLD_SECONDS)
                for order in orders:
                    await repo.set_status(order.id, OrderStatus.out_for_delivery)
                    print(f"[delivery_job] Order {order.order_code} → out_for_delivery")
        except Exception as exc:
            print(f"[delivery_job] Error: {exc}")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
