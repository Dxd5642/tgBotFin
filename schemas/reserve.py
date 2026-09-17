from aiogram.fsm.state import StatesGroup, State

class CreateReserveBudget(StatesGroup):
    waiting_cat = State()
    waiting_balance = State()
    waiting_date = State()

class DeleteReserveBudget(StatesGroup):
    waiting_action = State()
    action_true = State()
    action_false = State()

class ChangeDateReserveBudget(StatesGroup):
    waiting_date = State()

class AddingAmountReserveBudget(StatesGroup):
    waiting_date = State()

    