from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.database import Product, Order, User  # اضافه کردن import های مورد نیاز

class NotificationService:
    def __init__(self, session: Session, bot):
        self.session = session
        self.bot = bot

    async def notify_admins(
        self,
        message: str,
        notification_type: str = 'info'
    ):
        admin_ids = self.bot.get('config').tg_bot.admin_ids
        for admin_id in admin_ids:
            try:
                await self.bot.send_message(
                    admin_id,
                    f"🔔 {notification_type.upper()}\n\n{message}"
                )
            except:
                continue

    async def notify_low_stock(self, product: Product):
        message = (
            f"⚠️ هشدار موجودی کم\n\n"
            f"محصول: {product.name}\n"
            f"موجودی فعلی: {product.stock}"
        )
        await self.notify_admins(message, 'warning')

    async def notify_new_order(self, order: Order):
        message = (
            f"🛍 سفارش جدید\n\n"
            f"شماره سفارش: #{order.id}\n"
            f"کاربر: {order.user.username or order.user_id}\n"
            f"مبلغ: {order.amount:,} تومان"
        )
        await self.notify_admins(message, 'order')

    async def notify_user(
        self,
        user_id: int,
        message: str,
        notification_type: str = 'info'
    ):
        try:
            await self.bot.send_message(
                user_id,
                f"🔔 {message}"
            )
            return True
        except:
            return False
