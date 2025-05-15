from aiogram.fsm.state import StatesGroup, State

class SupportTicket(StatesGroup):
    waiting_for_message = State()

class AdminSupport(StatesGroup):
    waiting_for_reply = State()
