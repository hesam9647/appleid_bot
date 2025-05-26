from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.settings_service import SettingsService
from app.keyboards.admin_kb import admin_settings_kb

router = Router()

class SettingsStates(StatesGroup):
    waiting_for_welcome_text = State()
    waiting_for_rules_text = State()
    waiting_for_help_text = State()
    waiting_for_rate_limit = State()
    waiting_for_min_deposit = State()

@router.callback_query(F.data == "admin_settings")
async def show_settings_menu(callback: CallbackQuery):
    settings_service = SettingsService(callback.bot.get('db_session'))
    settings = await settings_service.get_all_settings()
    
    text = "⚙️ تنظیمات ربات:\n\n"
    text += f"🔄 محدودیت درخواست: {settings.get('rate_limit', '10')} در دقیقه\n"
    text += f"💰 حداقل شارژ: {settings.get('min_deposit', '10000')} تومان\n"
    text += f"✅ خرید: {'فعال' if settings.get('purchase_enabled', 'true') == 'true' else 'غیرفعال'}\n"
    text += f"💬 تیکت: {'فعال' if settings.get('ticket_enabled', 'true') == 'true' else 'غیرفعال'}\n"
    text += f"💰 کیف پول: {'فعال' if settings.get('wallet_enabled', 'true') == 'true' else 'غیرفعال'}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_settings_kb()
    )

@router.callback_query(F.data == "admin_edit_texts")
async def show_texts_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📝 ویرایش متن‌ها\n"
        "لطفاً متن مورد نظر برای ویرایش را انتخاب کنید:",
        reply_markup=admin_texts_kb()
    )

@router.callback_query(F.data == "admin_edit_welcome")
async def edit_welcome_text(callback: CallbackQuery, state: FSMContext):
    settings_service = SettingsService(callback.bot.get('db_session'))
    current_text = await settings_service.get_text('welcome')
    
    await callback.message.edit_text(
        f"متن فعلی خوش‌آمدگویی:\n\n{current_text}\n\n"
        "متن جدید را وارد کنید:"
    )
    await state.set_state(SettingsStates.waiting_for_welcome_text)

@router.message(SettingsStates.waiting_for_welcome_text)
async def process_welcome_text(message: Message, state: FSMContext):
    settings_service = SettingsService(message.bot.get('db_session'))
    await settings_service.set_text('welcome', message.text)
    
    await message.answer("✅ متن خوش‌آمدگویی با موفقیت بروزرسانی شد.")
    await state.clear()

@router.callback_query(F.data.startswith("admin_toggle_"))
async def toggle_feature(callback: CallbackQuery):
    feature = callback.data.replace("admin_toggle_", "")
    settings_service = SettingsService(callback.bot.get('db_session'))
    
    current = await settings_service.get_setting(f"{feature}_enabled")
    new_value = "false" if current == "true" else "true"
    await settings_service.set_setting(f"{feature}_enabled", new_value)
    
    await show_settings_menu(callback)

@router.callback_query(F.data == "admin_set_rate_limit")
async def set_rate_limit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔄 تنظیم محدودیت درخواست\n"
        "لطفاً تعداد مجاز درخواست در دقیقه را وارد کنید:"
    )
    await state.set_state(SettingsStates.waiting_for_rate_limit)

@router.message(SettingsStates.waiting_for_rate_limit)
async def process_rate_limit(message: Message, state: FSMContext):
    try:
        limit = int(message.text)
        if limit < 1:
            raise ValueError
            
        settings_service = SettingsService(message.bot.get('db_session'))
        await settings_service.set_setting('rate_limit', str(limit))
        
        await message.answer("✅ محدودیت درخواست با موفقیت بروزرسانی شد.")
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")
    finally:
        await state.clear()
