from aiogram.fsm.state import StatesGroup, State

class Registr(StatesGroup):
    waiting_balance = State()
