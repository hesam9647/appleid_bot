from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional
from datetime import datetime

from app.database import DiscountCode, DiscountUsage

class DiscountService:
    def __init__(self, session: Session):
        self.session = session

    async def create_discount(self, 
                            code: str, 
                            discount_type: str,
                            discount_value: float,
                            max_uses: int,
                            expires_at: datetime) -> DiscountCode:
        discount = DiscountCode(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            max_uses=max_uses,
            expires_at=expires_at
        )
        self.session.add(discount)
        await self.session.commit()
        return discount

    async def validate_discount(self, code: str, user_id: int) -> tuple[bool, str, Optional[float]]:
        result = await self.session.execute(
            select(DiscountCode).where(DiscountCode.code == code)
        )
        discount = result.scalar_one_or_none()
        
        if not discount:
            return False, "کد تخفیف نامعتبر است", None
            
        if not discount.is_active:
            return False, "این کد تخفیف غیرفعال شده است", None
            
        if discount.expires_at and discount.expires_at < datetime.utcnow():
            return False, "این کد تخفیف منقضی شده است", None
            
        if discount.used_count >= discount.max_uses:
            return False, "ظرفیت استفاده از این کد تخفیف تکمیل شده است", None
            
        # Check if user has already used this code
        result = await self.session.execute(
            select(DiscountUsage)
            .where(
                DiscountUsage.code_id == discount.id,
                DiscountUsage.user_id == user_id
            )
        )
        if result.scalar_one_or_none():
            return False, "شما قبلاً از این کد تخفیف استفاده کرده‌اید", None

        return True, "کد تخفیف معتبر است", discount.discount_value

    async def use_discount(self, code: str, user_id: int) -> bool:
        result = await self.session.execute(
            select(DiscountCode).where(DiscountCode.code == code)
        )
        discount = result.scalar_one_or_none()
        
        if not discount:
            return False
            
        usage = DiscountUsage(
            code_id=discount.id,
            user_id=user_id
        )
        self.session.add(usage)
        
        discount.used_count += 1
        await self.session.commit()
        return True
