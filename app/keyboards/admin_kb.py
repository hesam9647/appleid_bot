from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 مدیریت کاربران", callback_data="admin_users_manage")
    builder.button(text="📦 مدیریت محصولات", callback_data="admin_products")
    builder.button(text="💬 تیکت‌ها", callback_data="admin_tickets")
    builder.button(text="📊 آمار و گزارشات", callback_data="admin_stats")
    builder.button(text="✉️ ارسال پیام", callback_data="admin_broadcast")
    builder.button(text="⚙️ تنظیمات", callback_data="admin_settings")
    builder.adjust(2)
    return builder.as_markup()

def admin_users_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 جستجوی کاربر", callback_data="admin_user_search")
    builder.button(text="📋 لیست کاربران", callback_data="admin_users_list")
    builder.button(text="✅ کاربران فعال", callback_data="admin_active_users")
    builder.button(text="❌ کاربران مسدود", callback_data="admin_blocked_users")
    builder.button(text="💰 کاربران پردرآمد", callback_data="admin_top_users")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()

def admin_user_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚫 مسدود کردن", callback_data=f"admin_user_block_{user_id}")
    builder.button(text="✅ رفع مسدودی", callback_data=f"admin_user_unblock_{user_id}")
    builder.button(text="💰 تغییر موجودی", callback_data=f"admin_user_balance_{user_id}")
    builder.button(text="📝 افزودن یادداشت", callback_data=f"admin_user_note_{user_id}")
    builder.button(text="📊 آمار کاربر", callback_data=f"admin_user_stats_{user_id}")
    builder.button(text="🔙 بازگشت", callback_data="admin_users_manage")
    builder.adjust(2)
    return builder.as_markup()

def admin_appleid_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📤 آپلود فایل جدید", callback_data="admin_upload_new")
    builder.button(text="📊 وضعیت موجودی", callback_data="admin_stock")
    builder.button(text="📋 لیست اپل‌آیدی‌ها", callback_data="admin_appleid_list")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()

def admin_pricing_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ افزودن تعرفه", callback_data="admin_add_price")
    builder.button(text="✏️ ویرایش تعرفه", callback_data="admin_edit_price")
    builder.button(text="❌ حذف تعرفه", callback_data="admin_delete_price")
    builder.button(text="🎁 کدهای تخفیف", callback_data="admin_discounts")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()

def admin_discount_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ کد تخفیف جدید", callback_data="admin_add_discount")
    builder.button(text="📋 لیست کدها", callback_data="admin_list_discounts")
    builder.button(text="❌ حذف کد", callback_data="admin_delete_discount")
    builder.button(text="🔙 بازگشت", callback_data="admin_pricing")
    builder.adjust(2)
    return builder.as_markup()

def admin_stats_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 آمار فروش", callback_data="admin_sales_stats")
    builder.button(text="👥 آمار کاربران", callback_data="admin_user_stats")
    builder.button(text="📦 آمار موجودی", callback_data="admin_inventory_stats")
    builder.button(text="💬 آمار پشتیبانی", callback_data="admin_support_stats")
    builder.button(text="📑 خروجی اکسل", callback_data="admin_export_report")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()

def admin_settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 ویرایش متن‌ها", callback_data="admin_edit_texts")
    builder.button(text="🔄 محدودیت درخواست", callback_data="admin_set_rate_limit")
    builder.button(text="💰 حداقل شارژ", callback_data="admin_set_min_deposit")
    builder.button(text="🛍 خرید", callback_data="admin_toggle_purchase")
    builder.button(text="💬 تیکت", callback_data="admin_toggle_ticket")
    builder.button(text="💰 کیف پول", callback_data="admin_toggle_wallet")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()

def admin_texts_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👋 خوش‌آمدگویی", callback_data="admin_edit_welcome")
    builder.button(text="📋 قوانین", callback_data="admin_edit_rules")
    builder.button(text="❓ راهنما", callback_data="admin_edit_help")
    builder.button(text="🔙 بازگشت", callback_data="admin_settings")
    builder.adjust(2)
    return builder.as_markup()

def admin_tickets_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📬 تیکت‌های باز", callback_data="admin_tickets_open")
    builder.button(text="📝 همه تیکت‌ها", callback_data="admin_tickets_all")
    builder.button(text="⚡️ اولویت بالا", callback_data="admin_tickets_high")
    builder.button(text="📊 آمار تیکت‌ها", callback_data="admin_tickets_stats")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()

def ticket_actions_kb(ticket_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ پاسخ", callback_data=f"admin_ticket_reply_{ticket_id}")
    builder.button(text="❌ بستن تیکت", callback_data=f"admin_ticket_close_{ticket_id}")
    builder.button(text="⚡️ اولویت بالا", callback_data=f"admin_ticket_priority_{ticket_id}_high")
    builder.button(text="📊 اولویت عادی", callback_data=f"admin_ticket_priority_{ticket_id}_normal")
    builder.button(text="🔙 بازگشت", callback_data="admin_tickets")
    builder.adjust(2)
    return builder.as_markup()

def broadcast_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 همه کاربران", callback_data="broadcast_all")
    builder.button(text="✅ کاربران فعال", callback_data="broadcast_active")
    builder.button(text="💰 کاربران خریدار", callback_data="broadcast_with_purchase")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()

def admin_products_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ افزودن محصول", callback_data="admin_add_product")
    builder.button(text="📝 ویرایش محصول", callback_data="admin_edit_product")
    builder.button(text="❌ حذف محصول", callback_data="admin_delete_product")
    builder.button(text="💰 قیمت‌گذاری", callback_data="admin_pricing")
    builder.button(text="📦 موجودی", callback_data="admin_stock")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()

def admin_reports_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 گزارش فروش", callback_data="admin_report_sales")
    builder.button(text="📊 گزارش محصولات", callback_data="admin_report_products")
    builder.button(text="👥 گزارش کاربران", callback_data="admin_report_users")
    builder.button(text="📑 خروجی اکسل", callback_data="admin_report_excel")
    builder.button(text="🔙 بازگشت", callback_data="admin_main")
    builder.adjust(2)
    return builder.as_markup()
