from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.ticket_service import TicketService
from app.keyboards.admin_kb import admin_tickets_kb, ticket_actions_kb

router = Router()

class TicketStates(StatesGroup):
    waiting_for_reply = State()

@router.callback_query(F.data == "admin_tickets")
async def show_tickets_menu(callback: CallbackQuery):
    ticket_service = TicketService(callback.bot.get('db_session'))
    open_tickets = await ticket_service.get_open_tickets()
    
    text = "💬 مدیریت تیکت‌ها\n\n"
    text += f"📬 تیکت‌های باز: {len(open_tickets)}\n\n"
    
    if open_tickets:
        text += "تیکت‌های اخیر:\n"
        for ticket in open_tickets[:5]:  # Show last 5 tickets
            text += f"🎫 #{ticket.id} - {ticket.title}\n"
            text += f"👤 کاربر: {ticket.user.username or ticket.user_id}\n"
            text += f"⏰ {ticket.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
            text += f"🔵 وضعیت: {ticket.status}\n\n"
    
    await callback.message.edit_text(text, reply_markup=admin_tickets_kb())

@router.callback_query(F.data.startswith("admin_ticket_view_"))
async def view_ticket(callback: CallbackQuery):
    ticket_id = int(callback.data.split('_')[-1])
    ticket_service = TicketService(callback.bot.get('db_session'))
    
    ticket = await ticket_service.get_ticket(ticket_id)
    if not ticket:
        await callback.answer("❌ تیکت مورد نظر یافت نشد!", show_alert=True)
        return
    
    messages = await ticket_service.get_ticket_messages(ticket_id)
    
    text = f"🎫 تیکت #{ticket.id}\n"
    text += f"📝 موضوع: {ticket.title}\n"
    text += f"👤 کاربر: {ticket.user.username or ticket.user_id}\n"
    text += f"⏰ ایجاد: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}\n"
    text += f"🔵 وضعیت: {ticket.status}\n"
    text += f"⚡️ اولویت: {ticket.priority}\n\n"
    text += "📨 پیام‌ها:\n\n"
    
    for msg in messages:
        sender = "🔷 ادمین" if msg.is_from_admin else "🔶 کاربر"
        text += f"{sender}: {msg.content}\n"
        text += f"⏰ {msg.created_at.strftime('%H:%M')}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=ticket_actions_kb(ticket_id)
    )

@router.callback_query(F.data.startswith("admin_ticket_reply_"))
async def reply_to_ticket(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split('_')[-1])
    await state.update_data(ticket_id=ticket_id)
    
    await callback.message.edit_text(
        "✏️ لطفاً پاسخ خود را وارد کنید:"
    )
    await state.set_state(TicketStates.waiting_for_reply)

@router.message(TicketStates.waiting_for_reply)
async def process_ticket_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = data['ticket_id']
    
    ticket_service = TicketService(message.bot.get('db_session'))
    await ticket_service.add_message(
        ticket_id=ticket_id,
        sender_id=message.from_user.id,
        content=message.text,
        is_from_admin=True
    )
    
    # Notify user about new reply
    ticket = await ticket_service.get_ticket(ticket_id)
    await message.bot.send_message(
        ticket.user_id,
        f"🔔 پاسخ جدید برای تیکت #{ticket_id}\n\n"
        f"پاسخ ادمین:\n{message.text}"
    )
    
    await message.answer("✅ پاسخ شما با موفقیت ارسال شد.")
    await state.clear()

@router.callback_query(F.data.startswith("admin_ticket_close_"))
async def close_ticket(callback: CallbackQuery):
    ticket_id = int(callback.data.split('_')[-1])
    ticket_service = TicketService(callback.bot.get('db_session'))
    
    if await ticket_service.close_ticket(ticket_id):
        await callback.answer("✅ تیکت با موفقیت بسته شد.")
        # Notify user
        ticket = await ticket_service.get_ticket(ticket_id)
        await callback.bot.send_message(
            ticket.user_id,
            f"🔔 تیکت #{ticket_id} بسته شد."
        )
    else:
        await callback.answer("❌ خطا در بستن تیکت!", show_alert=True)

@router.callback_query(F.data.startswith("admin_ticket_priority_"))
async def set_ticket_priority(callback: CallbackQuery):
    data = callback.data.split('_')
    ticket_id = int(data[-2])
    priority = data[-1]
    
    ticket_service = TicketService(callback.bot.get('db_session'))
    if await ticket_service.set_priority(ticket_id, priority):
        await callback.answer(f"✅ اولویت تیکت به {priority} تغییر کرد.")
    else:
        await callback.answer("❌ خطا در تغییر اولویت!", show_alert=True)
