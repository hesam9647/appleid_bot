from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional
import pandas as pd
from datetime import datetime

from app.database import AppleID

class AppleIDService:
    def __init__(self, session: Session):
        self.session = session

    async def add_apple_id(self, email: str, password: str, price: float) -> AppleID:
        apple_id = AppleID(
            email=email,
            password=password,
            price=price
        )
        self.session.add(apple_id)
        await self.session.commit()
        return apple_id

    async def bulk_add_apple_ids(self, excel_path: str, price: float) -> tuple[int, list[str]]:
        try:
            df = pd.read_excel(excel_path)
            success_count = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    await self.add_apple_id(
                        email=str(row['email']),
                        password=str(row['password']),
                        price=price
                    )
                    success_count += 1
                except Exception as e:
                    errors.append(f"خطا در افزودن {row['email']}: {str(e)}")
            
            return success_count, errors
        except Exception as e:
            return 0, [f"خطا در خواندن فایل اکسل: {str(e)}"]

    async def get_available_apple_ids(self) -> List[AppleID]:
        result = await self.session.execute(
            select(AppleID)
            .where(AppleID.is_sold == False)
            .order_by(AppleID.created_at)
        )
        return result.scalars().all()

    async def get_apple_id_by_id(self, id: int) -> Optional[AppleID]:
        result = await self.session.execute(
            select(AppleID).where(AppleID.id == id)
        )
        return result.scalar_one_or_none()

    async def mark_as_sold(self, id: int, user_id: int) -> bool:
        try:
            await self.session.execute(
                update(AppleID)
                .where(AppleID.id == id)
                .values(is_sold=True, sold_to=user_id)
            )
            await self.session.commit()
            return True
        except:
            return False

    async def get_stock_stats(self) -> dict:
        total = await self.session.scalar(select(func.count(AppleID.id)))
        available = await self.session.scalar(
            select(func.count(AppleID.id))
            .where(AppleID.is_sold == False)
        )
        sold = await self.session.scalar(
            select(func.count(AppleID.id))
            .where(AppleID.is_sold == True)
        )
        
        return {
            "total": total,
            "available": available,
            "sold": sold
        }
