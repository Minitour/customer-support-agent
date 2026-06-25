import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.db.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus

HERE = os.path.dirname(os.path.abspath(__file__))

DATA = "/app/.data"


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)

async def seed_users():
    for u in load("users.json")["users"]:
        async with AsyncSessionLocal() as db:
            if await db.scalar(select(User).where(User.email == u["email"])):
                continue
            db.add(User(email=u["email"], name=u["name"], hashed_password=hash_password(u["password"])))
            await db.commit()
    print("Users created.")


async def seed_orders():
    for o in load("orders.json")["orders"]:
        async with AsyncSessionLocal() as db:
            if await db.scalar(select(Order).where(Order.order_code == o["order_code"])):
                continue
            user = await db.scalar(select(User).where(User.email == o["user_email"]))
            if not user:
                continue
            total = sum(i["unit_price"] * i["quantity"] for i in o["items"])
            order = Order(
                order_code=o["order_code"],
                user_id=user.id,
                status=OrderStatus(o["status"]),
                carrier=o.get("carrier"),
                tracking=o.get("tracking"),
                eta=datetime.now(timezone.utc) + timedelta(days=o.get("days_from_now_eta", 4)),
                total=total,
            )
            db.add(order)
            await db.flush()
            for i in o["items"]:
                db.add(OrderItem(order_id=order.id, product_id=i["product_id"], quantity=i["quantity"], unit_price=i["unit_price"]))
            await db.commit()
    print("Orders created.")


async def clear():
    async with AsyncSessionLocal() as db:
        await db.execute(delete(OrderItem))
        await db.execute(delete(Order))
        await db.execute(delete(User))
        await db.commit()
    print("Database cleared.")


async def main(mode):
    if mode == "create":
        await seed_users()
        await seed_orders()
    elif mode == "clear":
        await clear()
    elif mode == "reset":
        await clear()
        await seed_users()
        await seed_orders()
    else:
        print("Usage: python -m tests.create_cases [create|clear|reset]")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "create"))