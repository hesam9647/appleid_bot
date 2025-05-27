from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta

from app.services.report_service import ReportService
from app.keyboards.admin_kb import admin_reports_kb

router = Router()

@router.callback_query(F.data == "admin_reports")
async def show_reports_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📊 گزارش‌ها و آمار\n"
        "لطفاً نوع گزارش را انتخاب کنید:",
        reply_markup=admin_reports_kb()
    )

@router.callback_query(F.data == "admin_report_sales")
async def show_sales_report(callback: CallbackQuery):
    report_service = ReportService(callback.bot.get('db_session'))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    report = await report_service.generate_sales_report(start_date, end_date)
    
    # Send chart
    await callback.message.answer_photo(
        report['chart'],
        caption=(
            "📊 گزارش فروش 30 روز گذشته\n\n"
            f"💰 مجموع فروش: {report['total_sales']:,} تومان\n"
            f"📦 تعداد فروش: {report['total_count']}\n"
            f"📈 میانگین روزانه: {report['average_daily']:,} تومان"
        ),
        reply_markup=admin_reports_kb()
    )
