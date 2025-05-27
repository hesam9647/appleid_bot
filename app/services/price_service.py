from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import Optional, Dict
import aiohttp
import json
from datetime import datetime

from app.database import Payment, Transaction, User

class PaymentService:
    def __init__(self, session: Session, merchant_id: str, callback_url: str):
        self.session = session
        self.merchant_id = merchant_id
        self.callback_url = callback_url
        self.zarinpal_request_url = "https://api.zarinpal.com/pg/v4/payment/request.json"
        self.zarinpal_verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"

    async def create_payment(self, user_id: int, amount: int, description: str) -> Optional[Dict]:
        try:
            # Create payment record
            payment = Payment(
                user_id=user_id,
                amount=amount,
                description=description,
                status='pending'
            )
            self.session.add(payment)
            await self.session.flush()

            # Request payment URL from Zarinpal
            async with aiohttp.ClientSession() as session:
                payload = {
                    "merchant_id": self.merchant_id,
                    "amount": amount,
                    "description": description,
                    "callback_url": f"{self.callback_url}?payment_id={payment.id}",
                }
                
                async with session.post(self.zarinpal_request_url, json=payload) as response:
                    result = await response.json()
                    
                    if result['data']['code'] == 100:
                        payment.authority = result['data']['authority']
                        await self.session.commit()
                        return {
                            'payment_id': payment.id,
                            'payment_url': f"https://www.zarinpal.com/pg/StartPay/{result['data']['authority']}"
                        }
            
            return None
        except Exception as e:
            print(f"Payment creation error: {e}")
            return None

    async def verify_payment(self, payment_id: int, authority: str) -> bool:
        payment = await self.get_payment(payment_id)
        if not payment or payment.status != 'pending':
            return False

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "merchant_id": self.merchant_id,
                    "amount": payment.amount,
                    "authority": authority
                }
                
                async with session.post(self.zarinpal_verify_url, json=payload) as response:
                    result = await response.json()
                    
                    if result['data']['code'] == 100:
                        # Update payment status
                        payment.status = 'completed'
                        payment.ref_id = result['data']['ref_id']
                        
                        # Create transaction
                        transaction = Transaction(
                            user_id=payment.user_id,
                            amount=payment.amount,
                            type='deposit',
                            payment_id=payment.id
                        )
                        self.session.add(transaction)
                        
                        # Update user balance
                        user = await self.session.execute(
                            select(User).where(User.id == payment.user_id)
                        )
                        user = user.scalar_one()
                        user.balance += payment.amount
                        
                        await self.session.commit()
                        return True
                    
                    payment.status = 'failed'
                    await self.session.commit()
                    return False
                    
        except Exception as e:
            print(f"Payment verification error: {e}")
            return False

    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_user_payments(self, user_id: int) -> list[Payment]:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        return result.scalars().all()
