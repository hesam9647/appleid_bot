from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
import asyncio
from datetime import datetime

from app.database import User, BroadcastMessage

class BroadcastService:
    def __init__(self, session: Session):
        self.session = session

    async def create_broadcast(
        self,
        sender_id: int,
        message_text: str,
        media_type: Optional[str] = None,
        media_id: Optional[str] = None,
        target_type: str = 'all',  # all, active, with_purchase
        button_text: Optional[str] = None,
        button_url: Optional[str] = None
    ) -> BroadcastMessage:
        broadcast = BroadcastMessage(
            sender_id=sender_id,
            message_text=message_text,
            media_type=media_type,
            media_id=media_id,
            target_type=target_type,
            button_text=button_text,
            button_url=button_url,
            status='pending'
        )
        self.session.add(broadcast)
        await self.session.commit()
        return broadcast

    async def get_target_users(self, target_type: str) -> List[int]:
        query = select(User.user_id)
        
        if target_type == 'active':
            query = query.where(User.is_blocked == False)
        elif target_type == 'with_purchase':
            query = query.join(User.transactions).where(User.is_blocked == False)
            
        result = await self.session.execute(query)
        return result.scalars().all()

    async def send_broadcast(
        self,
        bot,
        broadcast_id: int,
        chunk_size: int = 30,
        delay: float = 0.05
    ) -> dict:
        broadcast = await self.session.get(BroadcastMessage, broadcast_id)
        if not broadcast or broadcast.status != 'pending':
            return {'success': 0, 'failed': 0}

        users = await self.get_target_users(broadcast.target_type)
        success_count = 0
        failed_count = 0

        # Create keyboard if button exists
        keyboard = None
        if broadcast.button_text and broadcast.button_url:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text=broadcast.button_text,
                        url=broadcast.button_url
                    )
                ]]
            )

        # Send messages in chunks
        for i in range(0, len(users), chunk_size):
            chunk = users[i:i + chunk_size]
            tasks = []
            
            for user_id in chunk:
                try:
                    if broadcast.media_type == 'photo':
                        tasks.append(bot.send_photo(
                            user_id,
                            broadcast.media_id,
                            caption=broadcast.message_text,
                            reply_markup=keyboard
                        ))
                    elif broadcast.media_type == 'video':
                        tasks.append(bot.send_video(
                            user_id,
                            broadcast.media_id,
                            caption=broadcast.message_text,
                            reply_markup=keyboard
                        ))
                    else:
                        tasks.append(bot.send_message(
                            user_id,
                            broadcast.message_text,
                            reply_markup=keyboard
                        ))
                except Exception as e:
                    print(f"Failed to send to {user_id}: {e}")
                    failed_count += 1
                    continue

            # Execute chunk
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count += len([r for r in results if not isinstance(r, Exception)])
            failed_count += len([r for r in results if isinstance(r, Exception)])
            
            # Delay between chunks
            await asyncio.sleep(delay)

        # Update broadcast status
        broadcast.status = 'completed'
        broadcast.completed_at = datetime.utcnow()
        broadcast.success_count = success_count
        broadcast.failed_count = failed_count
        await self.session.commit()

        return {
            'success': success_count,
            'failed': failed_count
        }
