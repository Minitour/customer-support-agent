from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Product))
        return result.scalar_one()

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def list(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Product], int]:
        query = select(Product)
        count_query = select(func.count()).select_from(Product)

        if category:
            query = query.where(Product.category == category)
            count_query = count_query.where(Product.category == category)
        if search:
            like = f"%{search}%"
            query = query.where(Product.title.ilike(like))
            count_query = count_query.where(Product.title.ilike(like))

        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all(), total

    async def get_categories(self) -> List[str]:
        result = await self.db.execute(
            select(Product.category).distinct().order_by(Product.category)
        )
        return [r for r in result.scalars().all() if r]

    async def bulk_create(self, products: List[dict]) -> None:
        objs = [Product(**p) for p in products]
        self.db.add_all(objs)
        await self.db.commit()
