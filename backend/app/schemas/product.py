from typing import Optional
from pydantic import BaseModel


class Review(BaseModel):
    rating: Optional[float] = None
    comment: Optional[str] = None
    date: Optional[str] = None
    reviewerName: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    discount_percentage: float
    rating: float
    stock: int
    brand: Optional[str] = None
    sku: Optional[str] = None
    thumbnail: Optional[str] = None
    warranty_information: Optional[str] = None
    shipping_information: Optional[str] = None
    return_policy: Optional[str] = None
    images: Optional[list[str]] = None
    reviews: Optional[list[Review]] = None

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int
