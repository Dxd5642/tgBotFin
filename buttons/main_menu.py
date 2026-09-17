from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from categories import CATEGORIES_KEYWORDS


def get_btn_menu():
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="📊 Аналитика за месяц", callback_data="analytic_month"),
        InlineKeyboardButton(text="💳 Мой баланс", callback_data="my_balance"),
        InlineKeyboardButton(text="🔏 Зарезервированные счета", callback_data="reserve_budget"),
        InlineKeyboardButton(text="📔 Заказать отчет по чекам за этот месяц", callback_data="report_order"),
        InlineKeyboardButton(text="📜 Последние операции", callback_data="last_checks"),
        # InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
    )

    builder.adjust(1)

    return builder.as_markup()


def get_btn_back():
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="Вернуться назад", callback_data="back"),
    )

    return builder.as_markup()


def get_btn_for_just_message():
    builder = InlineKeyboardBuilder()
        
    builder.add(
        InlineKeyboardButton(text="📊 Аналитика за месяц", callback_data="analytic_month"),
    )

    return builder.as_markup()

