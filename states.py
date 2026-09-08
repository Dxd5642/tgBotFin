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
    waiting_cat = State()
    waiting_balance = State()
    waiting_date = State()

class DeketeReserveBudget(StatesGroup):
    waiting_action = State()
    action_true = State()
    action_false = State()

class ChangeDateReserveBudget(StatesGroup):
    waiting_date = State()

class AddingAmountReserveBudget(StatesGroup):
    waiting_date = State()

    