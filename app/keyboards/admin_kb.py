from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("مدیریت کاربران", callback_data="admin_users"),
        InlineKeyboardButton("مدیریت اپل‌آیدی‌ها", callback_data="admin_apple_ids"),
    )
    kb.add(
        InlineKeyboardButton("ارسال پیام به همه", callback_data="admin_broadcast"),
        InlineKeyboardButton("وضعیت سرویس", callback_data="admin_toggle_service"),
    )
    return kb

def users_list_kb(users):
    kb = InlineKeyboardMarkup(row_width=1)
    for user_id, username, wallet, blocked in users:
        name = username or str(user_id)
        status = "🚫" if blocked else "✅"
        kb.insert(InlineKeyboardButton(f"{name} ({status})", callback_data=f"user_{user_id}"))
    kb.add(InlineKeyboardButton("بازگشت", callback_data="admin_main"))
    return kb

def user_manage_kb(user_id: int, blocked: bool):
    kb = InlineKeyboardMarkup(row_width=2)
    if blocked:
        kb.insert(InlineKeyboardButton("بازکردن بلاک", callback_data=f"unblock_{user_id}"))
    else:
        kb.insert(InlineKeyboardButton("بلاک کردن", callback_data=f"block_{user_id}"))
    kb.insert(InlineKeyboardButton("بازگشت", callback_data="admin_users"))
    return kb

def apple_ids_manage_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("افزودن اپل‌آیدی متنی", callback_data="add_apple_text"),
        InlineKeyboardButton("افزودن اپل‌آیدی از فایل اکسل", callback_data="add_apple_excel"),
        InlineKeyboardButton("بازگشت", callback_data="admin_main"),
    )
    return kb

def toggle_service_kb(service_active: bool):
    kb = InlineKeyboardMarkup(row_width=1)
    text = "خاموش کردن فروش" if service_active else "روشن کردن فروش"
    kb.add(InlineKeyboardButton(text, callback_data="toggle_service"))
    kb.add(InlineKeyboardButton("بازگشت", callback_data="admin_main"))
    return kb

def payment_approve_kb(purchase_id: int):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("تایید پرداخت", callback_data=f"approve_payment_{purchase_id}"),
        InlineKeyboardButton("رد پرداخت", callback_data=f"reject_payment_{purchase_id}"),
    )
    return kb
