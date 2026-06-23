import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.database import engine, Base, AsyncSessionLocal
from app.models import User, Product, Order, OrderItem  # ensure models are registered
from app.repositories.product_repository import ProductRepository
from app.vectorstore.ingestion import ingest_policy_if_empty, ingest_products_if_empty
from app.jobs.delivery_job import delivery_transition_loop
from app.api.routes import auth, products, orders, chat

STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed relational DB
    async with AsyncSessionLocal() as db:
        repo = ProductRepository(db)
        count = await repo.count()
        if count == 0:
            try:
                with open(settings.PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                products_data = [
                    {
                        "id": p["id"],
                        "title": p["title"],
                        "description": p.get("description"),
                        "category": p.get("category"),
                        "price": p.get("price", 0),
                        "discount_percentage": p.get("discountPercentage", 0),
                        "rating": p.get("rating", 0),
                        "stock": p.get("stock", 0),
                        "brand": p.get("brand"),
                        "sku": p.get("sku"),
                        "thumbnail": p.get("thumbnail"),
                        "warranty_information": p.get("warrantyInformation"),
                        "shipping_information": p.get("shippingInformation"),
                        "return_policy": p.get("returnPolicy"),
                        "images": p.get("images"),
                        "reviews": p.get("reviews"),
                    }
                    for p in data.get("products", [])
                ]
                await repo.bulk_create(products_data)
                print(f"[startup] Seeded {len(products_data)} products to Postgres.")
            except Exception as exc:
                print(f"[startup] Failed to seed products: {exc}")

    # Seed vector stores
    try:
        await ingest_products_if_empty(settings.PRODUCTS_JSON_PATH)
        await ingest_policy_if_empty(settings.POLICY_DIR_PATH)
    except Exception as exc:
        print(f"[startup] Vector store ingestion error (non-fatal): {exc}")

    # Start background delivery job
    task = asyncio.create_task(delivery_transition_loop())

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


app = FastAPI(title="ShopEase Customer Support API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve the compiled React SPA — must be registered after all API routes.
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        """Return index.html for all non-API paths so the React router works."""
        return FileResponse(STATIC_DIR / "index.html")
