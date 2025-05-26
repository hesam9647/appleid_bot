from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io

from app.services.stats_service import StatsService
from app.keyboards.admin_kb import admin_stats_kb

router = Router()

@router.callback_query(F.data == "admin_stats")
async def show_stats_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📊 آمار و گزارشات\n"
        "لطفاً نوع گزارش مورد نظر خود را انتخاب کنید:",
        reply_markup=admin_stats_kb()
    )

@router.callback_query(F.data == "admin_sales_stats")
async def show_sales_stats(callback: CallbackQuery):
    stats_service = StatsService(callback.bot.get('db_session'))
    sales_stats = await stats_service.get_sales_stats()
    
    text = "📈 آمار فروش (30 روز گذشته):\n\n"
    text += f"💰 مجموع فروش: {sales_stats['total_sales']:,} تومان\n"
    text += f"📦 تعداد فروش: {sales_stats['total_count']} عدد\n"
    text += f"📊 میانگین روزانه: {sales_stats['average_daily']:,} تومان\n\n"
    
    # Create sales chart
    plt.figure(figsize=(10, 5))
    data = sales_stats['daily_data']
    plt.plot([d['date'] for d in data], [d['amount'] for d in data])
    plt.title('نمودار فروش روزانه')
    plt.xlabel('تاریخ')
    plt.ylabel('مبلغ (تومان)')
    
    # Save plot to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    await callback.message.answer_photo(
        buf,
        caption=text,
        reply_markup=admin_stats_kb()
    )

@router.callback_query(F.data == "admin_user_stats")
async def show_user_stats(callback: CallbackQuery):
    stats_service = StatsService(callback.bot.get('db_session'))
    user_stats = await stats_service.get_user_stats()
    
    text = "👥 آمار کاربران:\n\n"
    text += f"📊 کل کاربران: {user_stats['total_users']}\n"
    text += f"✅ کاربران فعال: {user_stats['active_users']}\n"
    text += f"🆕 کاربران جدید (24h): {user_stats['new_users_24h']}\n"
    text += f"💰 کاربران خریدار: {user_stats['users_with_purchase']}\n"
    text += f"📈 نرخ تبدیل: {user_stats['conversion_rate']}%"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_stats_kb()
    )

@router.callback_query(F.data == "admin_inventory_stats")
async def show_inventory_stats(callback: CallbackQuery):
    stats_service = StatsService(callback.bot.get('db_session'))
    inventory_stats = await stats_service.get_inventory_stats()
    
    text = "📦 آمار موجودی:\n\n"
    text += f"📊 کل اپل‌آیدی‌ها: {inventory_stats['total']}\n"
    text += f"✅ موجود: {inventory_stats['available']}\n"
    text += f"💰 فروخته شده: {inventory_stats['sold']}\n"
    text += f"📈 درصد فروش: {inventory_stats['sold_percentage']}%"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_stats_kb()
    )

@router.callback_query(F.data == "admin_support_stats")
async def show_support_stats(callback: CallbackQuery):
    stats_service = StatsService(callback.bot.get('db_session'))
    support_stats = await stats_service.get_support_stats()
    
    text = "💬 آمار پشتیبانی:\n\n"
    text += f"📊 کل تیکت‌ها: {support_stats['total_tickets']}\n"
    text += f"📝 تیکت‌های باز: {support_stats['open_tickets']}\n"
    text += f"⏱ میانگین زمان پاسخ: {support_stats['avg_response_time']} ساعت"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_stats_kb()
    )

@router.callback_query(F.data == "admin_export_report")
async def export_report(callback: CallbackQuery):
    stats_service = StatsService(callback.bot.get('db_session'))
    report_file = await stats_service.generate_excel_report()
    
    await callback.message.answer_document(
        document=FSInputFile(report_file),
        caption="📊 گزارش کامل 30 روز گذشته"
    )
