from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.broadcast_service import BroadcastService
from app.keyboards.admin_kb import broadcast_kb

router = Router()

class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_media = State()
    waiting_for_button = State()

@router.callback_query(F.data == "admin_broadcast")
async def broadcast_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "✉️ ارسال پیام گروهی\n"
        "لطفاً نوع پیام را انتخاب کنید:",
        reply_markup=broadcast_kb()
    )

@router.callback_query(F.data.startswith("broadcast_"))
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    broadcast_type = callback.data.split('_')[1]
    await state.update_data(broadcast_type=broadcast_type)
    
    await callback.message.edit_text(
        "📝 لطفاً متن پیام خود را وارد کنید:\n"
        "برای افزودن دکمه، در خط آخر پیام به این صورت وارد کنید:\n"
        "button:متن دکمه:لینک"
    )
    await state.set_state(BroadcastStates.waiting_for_message)

@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    text = message.text
    button_data = None
    
    # Check for button in message
    if "button:" in text:
        text, button_info = text.rsplit("button:", 1)
        try:
            button_text, button_url = button_info.strip().split(":", 1)
            button_data = {
                "text": button_text,
                "url": button_url
            }
        except:
            await message.answer("❌ فرمت دکمه نادرست است. لطفاً مجدداً تلاش کنید.")
            return

    data = await state.get_data()
    broadcast_service = BroadcastService(message.bot.get('db_session'))
    
    broadcast = await broadcast_service.create_broadcast(
        sender_id=message.from_user.id,
        message_text=text,
        target_type=data['broadcast_type'],
        button_text=button_data['text'] if button_data else None,
        button_url=button_data['url'] if button_data else None
    )
    
    # Start broadcasting
    result = await broadcast_service.send_broadcast(message.bot, broadcast.id)
    
    await message.answer(
        f"✅ پیام گروهی ارسال شد\n\n"
        f"📊 نتیجه:\n"
        f"✅ موفق: {result['success']}\n"
        f"❌ ناموفق: {result['failed']}"
    )
    await state.clear()
