from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.models.order import OrderStatus


class CartItem(BaseModel):
    product_id: int
    quantity: int


class CheckoutRequest(BaseModel):
    items: List[CartItem]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product_title: Optional[str] = None
    product_thumbnail: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    order_code: str
    status: OrderStatus
    carrier: Optional[str] = None
    tracking: Optional[str] = None
    eta: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    total: float
    created_at: datetime
    items: List[OrderItemResponse] = []

    model_config = {"from_attributes": True}
