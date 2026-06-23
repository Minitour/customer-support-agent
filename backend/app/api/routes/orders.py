from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import CheckoutRequest, OrderResponse, OrderItemResponse

router = APIRouter(prefix="/orders", tags=["orders"])


def _serialize_order(order) -> OrderResponse:
    items = []
    for item in order.items:
        items.append(
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                product_title=item.product.title if item.product else None,
                product_thumbnail=item.product.thumbnail if item.product else None,
            )
        )
    return OrderResponse(
        id=order.id,
        order_code=order.order_code,
        status=order.status,
        carrier=order.carrier,
        tracking=order.tracking,
        eta=order.eta,
        total=order.total,
        created_at=order.created_at,
        items=items,
    )


@router.post("", response_model=OrderResponse, status_code=201)
async def checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not body.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    product_repo = ProductRepository(db)
    order_items = []
    for ci in body.items:
        product = await product_repo.get_by_id(ci.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {ci.product_id} not found")
        if product.stock < ci.quantity:
            raise HTTPException(
                status_code=400, detail=f"Insufficient stock for {product.title}"
            )
        order_items.append(
            {"product_id": ci.product_id, "quantity": ci.quantity, "unit_price": product.price}
        )

    order_repo = OrderRepository(db)
    order = await order_repo.create(user_id=current_user.id, items=order_items)

    # Re-fetch with items loaded
    order = await order_repo.get_by_id(order.id, user_id=current_user.id)
    return _serialize_order(order)


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = OrderRepository(db)
    orders = await repo.list_for_user(current_user.id)
    return [_serialize_order(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = OrderRepository(db)
    order = await repo.get_by_id(order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = OrderRepository(db)
    order = await repo.cancel(order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(
            status_code=400, detail="Order not found or cannot be cancelled in its current state"
        )
    order = await repo.get_by_id(order.id, user_id=current_user.id)
    return _serialize_order(order)
