import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class OrderStatus(str, enum.Enum):
    created = "created"
    received = "received"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


# Linear lifecycle the background job promotes orders through, in order.
PROMOTION_SEQUENCE = [
    OrderStatus.created,
    OrderStatus.received,
    OrderStatus.processing,
    OrderStatus.shipped,
    OrderStatus.delivered,
]

# An order may be cancelled while in any state between created and processing
# (inclusive). Once shipped or delivered it can no longer be cancelled.
CANCELLABLE_STATUSES = (
    OrderStatus.created,
    OrderStatus.received,
    OrderStatus.processing,
)


def next_status(status: OrderStatus) -> Optional[OrderStatus]:
    """Return the next status in the lifecycle, or None if terminal/unknown."""
    try:
        idx = PROMOTION_SEQUENCE.index(status)
    except ValueError:
        return None
    if idx + 1 < len(PROMOTION_SEQUENCE):
        return PROMOTION_SEQUENCE[idx + 1]
    return None


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.created, nullable=False
    )
    carrier: Mapped[str] = mapped_column(String(100), nullable=True)
    tracking: Mapped[str] = mapped_column(String(200), nullable=True)
    eta: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="select"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
