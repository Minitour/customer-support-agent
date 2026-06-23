import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
    CANCELLABLE_STATUSES,
    PROMOTION_SEQUENCE,
)


def _generate_order_code() -> str:
    letters = random.choices(string.ascii_uppercase, k=1)
    digits = random.choices(string.digits, k=5)
    return "".join(letters + digits)


CARRIERS = ["DHL", "FedEx", "UPS", "USPS", "Amazon Logistics"]


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        query = select(Order).options(selectinload(Order.items).selectinload(OrderItem.product))
        query = query.where(Order.id == order_id)
        if user_id is not None:
            query = query.where(Order.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, order_code: str, user_id: Optional[int] = None) -> Optional[Order]:
        query = select(Order).options(selectinload(Order.items).selectinload(OrderItem.product))
        query = query.where(Order.order_code == order_code)
        if user_id is not None:
            query = query.where(Order.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> List[Order]:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, user_id: int, items: list[dict]) -> Order:
        """items: list of {product_id, quantity, unit_price}"""
        code = _generate_order_code()
        # Ensure unique code
        while await self.get_by_code(code) is not None:
            code = _generate_order_code()

        carrier = random.choice(CARRIERS)
        tracking = "".join(random.choices(string.digits, k=12))
        eta = datetime.now(timezone.utc) + timedelta(days=random.randint(3, 7))
        total = sum(i["unit_price"] * i["quantity"] for i in items)

        order = Order(
            order_code=code,
            user_id=user_id,
            carrier=carrier,
            tracking=tracking,
            eta=eta,
            total=total,
            status=OrderStatus.created,
        )
        self.db.add(order)
        await self.db.flush()

        for item in items:
            self.db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                )
            )

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def cancel(self, order_id: int, user_id: int) -> Optional[Order]:
        order = await self.get_by_id(order_id, user_id=user_id)
        if order is None:
            return None
        if order.status not in CANCELLABLE_STATUSES:
            return None
        order.status = OrderStatus.cancelled
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_promotable(self) -> List[Order]:
        """Return all orders that can still advance to a later lifecycle stage
        (i.e. not yet delivered and not cancelled)."""
        promotable = [s for s in PROMOTION_SEQUENCE if s != OrderStatus.delivered]
        result = await self.db.execute(
            select(Order).where(Order.status.in_(promotable))
        )
        return result.scalars().all()

    async def set_status(self, order_id: int, status: OrderStatus) -> None:
        order = await self.db.get(Order, order_id)
        if order:
            order.status = status
            if status == OrderStatus.delivered:
                order.delivered_at = datetime.now(timezone.utc)
            await self.db.commit()
