from aiogram.fsm.state import StatesGroup, State

class AdminUserWallet(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()
