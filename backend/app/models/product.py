from sqlalchemy import String, Float, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    brand: Mapped[str] = mapped_column(String(255), nullable=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    thumbnail: Mapped[str] = mapped_column(Text, nullable=True)
    warranty_information: Mapped[str] = mapped_column(String(500), nullable=True)
    shipping_information: Mapped[str] = mapped_column(String(500), nullable=True)
    return_policy: Mapped[str] = mapped_column(String(500), nullable=True)
    images: Mapped[list] = mapped_column(JSON, nullable=True)
    reviews: Mapped[list] = mapped_column(JSON, nullable=True)

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product", lazy="select"
    )
