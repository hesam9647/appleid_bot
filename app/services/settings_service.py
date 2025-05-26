from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta

from app.database import BotSettings, BotText, RateLimit

class SettingsService:
    def __init__(self, session: Session):
        self.session = session
        self._cache = {}

    async def get_setting(self, key: str) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]
            
        result = await self.session.execute(
            select(BotSettings.value).where(BotSettings.key == key)
        )
        value = result.scalar_one_or_none()
        if value:
            self._cache[key] = value
        return value

    async def set_setting(self, key: str, value: str, description: str = None) -> bool:
        try:
            setting = await self.session.execute(
                select(BotSettings).where(BotSettings.key == key)
            )
            setting = setting.scalar_one_or_none()
            
            if setting:
                await self.session.execute(
                    update(BotSettings)
                    .where(BotSettings.key == key)
                    .values(value=value)
                )
            else:
                setting = BotSettings(key=key, value=value, description=description)
                self.session.add(setting)
                
            await self.session.commit()
            self._cache[key] = value
            return True
        except:
            return False

    async def get_text(self, key: str, **kwargs) -> str:
        result = await self.session.execute(
            select(BotText.text).where(BotText.key == key)
        )
        text = result.scalar_one_or_none()
        if text and kwargs:
            text = text.format(**kwargs)
        return text or f"Text not found: {key}"

    async def set_text(self, key: str, text: str, description: str = None) -> bool:
        try:
            bot_text = await self.session.execute(
                select(BotText).where(BotText.key == key)
            )
            bot_text = bot_text.scalar_one_or_none()
            
            if bot_text:
                await self.session.execute(
                    update(BotText)
                    .where(BotText.key == key)
                    .values(text=text)
                )
            else:
                bot_text = BotText(key=key, text=text, description=description)
                self.session.add(bot_text)
                
            await self.session.commit()
            return True
        except:
            return False

    async def check_rate_limit(self, user_id: int, action: str, max_requests: int, window_seconds: int) -> bool:
        now = datetime.utcnow()
        
        # Clean old records
        await self.session.execute(
            delete(RateLimit).where(RateLimit.reset_at < now)
        )
        
        result = await self.session.execute(
            select(RateLimit)
            .where(
                RateLimit.user_id == user_id,
                RateLimit.action == action
            )
        )
        rate_limit = result.scalar_one_or_none()
        
        if not rate_limit:
            rate_limit = RateLimit(
                user_id=user_id,
                action=action,
                count=1,
                reset_at=now + timedelta(seconds=window_seconds)
            )
            self.session.add(rate_limit)
            await self.session.commit()
            return True
            
        if rate_limit.count >= max_requests:
            return False
            
        rate_limit.count += 1
        await self.session.commit()
        return True

    async def get_all_settings(self) -> Dict[str, Any]:
        result = await self.session.execute(select(BotSettings))
        settings = result.scalars().all()
        return {s.key: s.value for s in settings}

    async def get_all_texts(self) -> Dict[str, str]:
        result = await self.session.execute(select(BotText))
        texts = result.scalars().all()
        return {t.key: t.text for t in texts}
