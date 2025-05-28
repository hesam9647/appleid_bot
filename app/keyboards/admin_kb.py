from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def admin_main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 مدیریت کاربران", callback_data="admin_users")
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
