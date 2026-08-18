from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from categories import CATEGORIES_KEYWORDS

from datetime import datetime

from database.database import get_all_checks, get_category_of_id

def get_btn_menu():
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="📊 Аналитика за месяц", callback_data="analytic_month"),
        InlineKeyboardButton(text="💳 Мой баланс", callback_data="my_balance"),
        InlineKeyboardButton(text="📔 Заказать отчет по чекам", callback_data="report_order"),
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


def get_orders_of_month(chat_id, current_page, ords_on_page = 5):
    start_idx = current_page * ords_on_page
    end_idx = start_idx + ords_on_page

    _, month, year = str(datetime.today().strftime("%d.%m.%Y")).split(".")
    all_orders = get_all_checks(chat_id, month, year)
    all_orders.reverse()

    orders = all_orders[start_idx:end_idx] if len(all_orders) > end_idx else all_orders[start_idx:]

    builder = InlineKeyboardBuilder()

    for order in orders:
        date = order[3].strftime("%d.%m.%Y %H:%M").split(" ")
        stat = "🟢" if order[0] != 0 else "🔴"
        builder.add(
            InlineKeyboardButton(
                text=f"{stat} Чек на {'+' if order[0] != 0 else '-'}{float(order[1]):,.0f} ₽ от {date[0]} {stat}",
                callback_data=f"view_desc_order_{order[5]}_page_{current_page}"
            )
        )

    if len(all_orders) >= end_idx:
        builder.add(InlineKeyboardButton(text="➡️ Следующая", callback_data=f"orders_page_{current_page+1}"))

    if current_page > 0:
        builder.add(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"orders_page_{current_page-1}"))

    builder.add(InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back"))


    builder.adjust(1)
    return builder.as_markup()

def get_orders_back(current_page):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="↩️ Вернуться к списку", callback_data=f"orders_page_{current_page}"))

    return builder.as_markup()
