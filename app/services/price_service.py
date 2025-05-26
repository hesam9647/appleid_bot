from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from typing import List, Optional
from datetime import datetime

from app.database import Price

class PriceService:
    def __init__(self, session: Session):
        self.session = session

    async def add_price(self, title: str, description: str, price: float) -> Price:
        price_obj = Price(
            title=title,
            description=description,
            price=price
        )
        self.session.add(price_obj)
        await self.session.commit()
        return price_obj

    async def get_active_prices(self) -> List[Price]:
        result = await self.session.execute(
            select(Price)
            .where(Price.is_active == True)
            .order_by(Price.price)
        )
        return result.scalars().all()

    async def update_price(self, price_id: int, **kwargs) -> bool:
        try:
            await self.session.execute(
                update(Price)
                .where(Price.id == price_id)
                .values(**kwargs)
            )
            await self.session.commit()
            return True
        except:
            return False

    async def delete_price(self, price_id: int) -> bool:
        try:
            await self.session.execute(
                delete(Price).where(Price.id == price_id)
            )
            await self.session.commit()
            return True
        except:
            return False
