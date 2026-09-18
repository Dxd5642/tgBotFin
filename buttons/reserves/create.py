from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.transactions.categories import CATEGORIES_KEYWORDS



def get_cat_for_create_reserve():
    builder = InlineKeyboardBuilder()

    for num, cat in enumerate(CATEGORIES_KEYWORDS):
            builder.add(
                InlineKeyboardButton(text=f"{num+1}. {cat}", callback_data=f"create_reserve_choise_cat_{num+1}"),
            )
    InlineKeyboardButton(text="❌ Отмена ❌", callback_data="create_reserve_choise_cat_cancel")
    
    builder.adjust(1)
    
    return builder.as_markup()



def get_cancel_btn_reserve():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="❌ Отмена ❌", callback_data="create_reserve_choise_cat_cancel"))

    return builder.as_markup()


def get_agree_btns_create_reserve():
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="✅ Все верно", callback_data="create_reserve_true"),
        InlineKeyboardButton(text="✏️ Редактировать", callback_data="create_reserve_edit"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="create_reserve_false"),
    )

    builder.adjust(1)
    return builder.as_markup()

