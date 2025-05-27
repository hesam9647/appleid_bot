from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional, Dict
from datetime import datetime

from app.database import Order, OrderItem, Product, User
from app.services.notification_service import NotificationService

class OrderService:
    def __init__(self, session: Session):
        self.session = session
        self.notification_service = NotificationService(session)

    async def create_order(
        self,
        user_id: int,
        items: List[Dict[str, int]]  # [{product_id: quantity}]
    ) -> Optional[Order]:
        try:
            # Calculate total amount and check stock
            total_amount = 0
            order_items = []
            
            for item in items:
                product = await self.session.get(Product, item['product_id'])
                if not product or product.stock < item['quantity']:
                    return None
                    
                total_amount += product.base_price * item['quantity']
                order_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'price': product.base_price
                })
            
            # Create order
            order = Order(
                user_id=user_id,
                total_amount=total_amount,
                status='pending'
            )
            self.session.add(order)
            await self.session.flush()
            
            # Add order items
            for item in order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item['product'].id,
                    quantity=item['quantity'],
                    price=item['price']
                )
                self.session.add(order_item)
                
                # Update stock
                item['product'].stock -= item['quantity']
            
            await self.session.commit()
            
            # Send notifications
            await self.notification_service.notify_new_order(order)
            
            return order
        except Exception as e:
            print(f"Error creating order: {e}")
            return None

    async def complete_order(self, order_id: int) -> bool:
        try:
            order = await self.session.get(Order, order_id)
            if not order or order.status != 'paid':
                return False
                
            order.status = 'completed'
            order.completed_at = datetime.utcnow()
            
            # Notify user
            await self.notification_service.notify_user(
                order.user_id,
                f"✅ سفارش #{order.id} شما تکمیل شد."
            )
            
            await self.session.commit()
            return True
        except:
            return False

    async def cancel_order(self, order_id: int) -> bool:
        try:
            order = await self.session.get(Order, order_id)
            if not order or order.status not in ['pending', 'paid']:
                return False
                
            # Restore stock
            for item in order.items:
                item.product.stock += item.quantity
            
            order.status = 'cancelled'
            
            # Notify user
            await self.notification_service.notify_user(
                order.user_id,
                f"❌ سفارش #{order.id} لغو شد."
            )
            
            await self.session.commit()
            return True
        except:
            return False
