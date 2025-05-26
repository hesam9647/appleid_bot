from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.appleid import AppleIDService
from app.services.excel_reader import ExcelReader
from app.keyboards.admin_kb import admin_appleid_kb

router = Router()

class AppleIDStates(StatesGroup):
    waiting_for_excel = State()
    waiting_for_price = State()

@router.callback_query(F.data == "admin_upload")
async def process_upload_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📁 آپلود اپل‌آیدی\n"
        "لطفاً فایل اکسل حاوی اپل‌آیدی‌ها را ارسال کنید.\n"
        "ساختار فایل باید شامل ستون‌های email و password باشد.",
        reply_markup=admin_appleid_kb()
    )
    await callback.message.answer_document(
        FSInputFile("templates/apple_id_template.xlsx"),
        caption="نمونه فایل اکسل را دانلود کنید"
    )

@router.message(F.document, AppleIDStates.waiting_for_excel)
async def process_excel_upload(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"downloads/{file_id}.xlsx"
    await message.bot.download_file(file.file_path, file_path)
    
    # Validate Excel structure
    is_valid, message_text = ExcelReader.validate_excel_structure(file_path)
    if not is_valid:
        await message.answer(f"❌ خطا در فایل: {message_text}")
        await state.clear()
        return
    
    await state.update_data(file_path=file_path)
    await message.answer("✅ فایل با موفقیت آپلود شد.\nلطفاً قیمت هر اپل‌آیدی را وارد کنید (به تومان):")
    await state.set_state(AppleIDStates.waiting_for_price)

@router.message(AppleIDStates.waiting_for_price)
async def process_price_input(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        data = await state.get_data()
        file_path = data['file_path']
        
        apple_id_service = AppleIDService(message.bot.get('db_session'))
        success_count, errors = await apple_id_service.bulk_add_apple_ids(file_path, price)
        
        response_text = f"✅ تعداد {success_count} اپل‌آیدی با موفقیت اضافه شد.\n"
        if errors:
            response_text += "\n❌ خطاها:\n" + "\n".join(errors)
        
        await message.answer(response_text)
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")
    finally:
        await state.clear()

@router.callback_query(F.data == "admin_stock")
async def process_stock_status(callback: CallbackQuery):
    apple_id_service = AppleIDService(callback.bot.get('db_session'))
    stats = await apple_id_service.get_stock_stats()
    
    await callback.message.edit_text(
        f"📊 وضعیت موجودی اپل‌آیدی:\n\n"
        f"📦 کل: {stats['total']}\n"
        f"✅ موجود: {stats['available']}\n"
        f"💰 فروخته شده: {stats['sold']}",
        reply_markup=admin_appleid_kb()
    )
