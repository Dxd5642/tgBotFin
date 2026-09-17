from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



def get_btns_delete_action_agree():
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="✅ Да, удалить", callback_data="reserve_action_delete_true"),
        InlineKeyboardButton(text="❌ Нет, не удалять", callback_data="reserve_action_delete_false")
    )
    builder.adjust(1)
    return builder.as_markup()
