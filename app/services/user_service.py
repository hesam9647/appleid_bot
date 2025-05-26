from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import User, Transaction

class UserService:
    def __init__(self, session: Session):
        self.session = session

    async def get_user(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_id: int, username: str = None) -> User:
        user = User(user_id=user_id, username=username)
        self.session.add(user)
        await self.session.commit()
        return user

    async def update_balance(self, user_id: int, amount: float) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        
        user.balance += amount
        await self.session.commit()
        return True

    async def block_user(self, user_id: int) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        
        user.is_blocked = True
        await self.session.commit()
        return True

    async def unblock_user(self, user_id: int) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        
        user.is_blocked = False
        await self.session.commit()
        return True

    async def get_active_users(self, days: int = 7) -> List[User]:
        date_threshold = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(User)
            .join(Transaction)
            .where(Transaction.created_at >= date_threshold)
            .group_by(User.id)
        )
        return result.scalars().all()

    async def get_user_stats(self) -> dict:
        total_users = await self.session.scalar(
            select(func.count(User.id))
        )
        active_users = await self.session.scalar(
            select(func.count(User.id))
            .where(User.is_blocked == False)
        )
        blocked_users = await self.session.scalar(
            select(func.count(User.id))
            .where(User.is_blocked == True)
        )
        
        return {
            "total": total_users,
            "active": active_users,
            "blocked": blocked_users
        }
