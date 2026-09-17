from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime

from database.database import get_all_checks



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
        stat = "🟢" if order[0] != 1 else "🔴"
        builder.add(
            InlineKeyboardButton(
                text=f"{stat} Чек на {'+' if order[0] != 1 else '-'}{float(order[1]):,.0f} ₽ от {date[0]} {stat}",
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
