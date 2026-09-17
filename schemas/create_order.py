from aiogram.fsm.state import StatesGroup, State

class AgreeCreateCheck(StatesGroup):
    waiting_action = State()
    action_true = State()
    action_false = State()
    action_edit = State()
    action_edit_category = State()
