from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from categories import CATEGORIES_KEYWORDS

def get_btn_for_create_check():
    builder = InlineKeyboardBuilder()
        
    builder.add(
        InlineKeyboardButton(text="✅ Все верно", callback_data="create_check_true"),
        InlineKeyboardButton(text="✏️ Редактировать", callback_data="create_check_edit"),
        InlineKeyboardButton(text="📝 Выбрать другую категорию", callback_data="create_check_category_edit"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="create_check_false"),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_btn_for_edit_cat():
    builder = InlineKeyboardBuilder()

    for num, cat in enumerate(CATEGORIES_KEYWORDS):
        builder.add(
            InlineKeyboardButton(text=f"{num+1}. {cat}", callback_data=f"create_check_cat_edit_{num+1}"),
        )

    builder.adjust(1)
    return builder.as_markup()
