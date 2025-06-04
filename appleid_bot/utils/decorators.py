# appleid_bot/utils/decorators.py

from telegram import Update
from telegram.ext import ContextTypes
from config.config import ADMIN_IDS
from functools import wraps

def admin_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id

        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔ شما به این بخش دسترسی ندارید.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped
