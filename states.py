from aiogram.fsm.state import StatesGroup, State

class Registr(StatesGroup):
    waiting_balance = State()

class AgreeCreateCheck(StatesGroup):
    waiting_action = State()
    action_true = State()
    action_false = State()
    action_edit = State()
    action_edit_category = State()

class CreateReserveBudget(StatesGroup):
    waiting_balance = State()