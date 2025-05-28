from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from typing import List, Optional
from datetime import datetime

from app.database import Product, ProductCategory

class ProductService:
    def __init__(self, session: Session):
        self.session = session

    async def get_active_products(self) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.name)
        )
        return result.scalars().all()

    async def get_product(self, product_id: int) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_products_by_category(self, category_id: int) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .where(
                Product.category_id == category_id,
                Product.is_active == True
            )
            .order_by(Product.name)
        )
        return result.scalars().all()

    async def search_products(self, query: str) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .where(
                Product.is_active == True,
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%")
                )
            )
            .order_by(Product.name)
        )
        return result.scalars().all()
