from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



def get_btn_cancel_change_date_reserv(res_id):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="❌ Отмена ❌", callback_data=f"cancel_change_date_for_reserve_{res_id}"))

    return builder.as_markup()

def get_btn_cancel_change_amount_reserv(res_id):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="❌ Отмена ❌", callback_data=f"cancel_change_amount_for_reserve_{res_id}"))

    return builder.as_markup()

def get_btn_retern_after_change_date_reserv(res_id):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="↩️ Вернуться назад", callback_data=f"get_reserve_by_id_{res_id}"))

    return builder.as_markup()

