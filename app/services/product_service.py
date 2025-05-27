from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from typing import List, Optional
from datetime import datetime

from app.database import Product, ProductCategory, ProductPrice

class ProductService:
    def __init__(self, session: Session):
        self.session = session

    async def create_product(
        self,
        name: str,
        description: str,
        category_id: int,
        base_price: float,
        stock: int = 0,
        is_active: bool = True
    ) -> Product:
        product = Product(
            name=name,
            description=description,
            category_id=category_id,
            base_price=base_price,
            stock=stock,
            is_active=is_active
        )
        self.session.add(product)
        await self.session.commit()
        return product

    async def update_stock(self, product_id: int, quantity: int) -> bool:
        try:
            product = await self.get_product(product_id)
            if not product:
                return False
            
            product.stock += quantity
            product.last_stock_update = datetime.utcnow()
            await self.session.commit()
            
            # Send notification if stock is low
            if product.stock < product.stock_alert_threshold:
                await self.notify_low_stock(product)
            
            return True
        except:
            return False

    async def get_product(self, product_id: int) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_active_products(self) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.category_id, Product.name)
        )
        return result.scalars().all()

    async def update_price(
        self,
        product_id: int,
        new_price: float,
        price_type: str = 'base'
    ) -> bool:
        try:
            if price_type == 'base':
                await self.session.execute(
                    update(Product)
                    .where(Product.id == product_id)
                    .values(base_price=new_price)
                )
            else:
                # Add special price
                price = ProductPrice(
                    product_id=product_id,
                    price=new_price,
                    type=price_type
                )
                self.session.add(price)
            
            await self.session.commit()
            return True
        except:
            return False
