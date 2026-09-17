from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_reserve_menu(reserves):
    builder = InlineKeyboardBuilder()

    for reserve in reserves:
        cat_name = reserve[-2]
        res_id = reserve[-1]
        builder.add(
            InlineKeyboardButton(text=f"💈 {cat_name}: {reserve[2].strftime('%d.%m.%y')} - {reserve[3].strftime('%d.%m.%y')} 📆", callback_data=f"get_reserve_by_id_{res_id}"),
        )

    builder.add(
        InlineKeyboardButton(text="✏️ Добавить новый счет", callback_data="create_new_reserve"),
        InlineKeyboardButton(text="↩️ Вернуться назад", callback_data="back")
    )

    builder.adjust(1)
    return builder.as_markup()


def get_btn_for_choised_reserve(reserv_id):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="➕ Пополнить резерв", callback_data=f"reserve_add_amount_{reserv_id}"),
        InlineKeyboardButton(text="📆 Продлить счет", callback_data=f"reserve_change_date_{reserv_id}"),
        InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"reserve_delete_{reserv_id}"),
        InlineKeyboardButton(text="↩️ Вернуться назад", callback_data="reserve_budget"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_btns_after_delete_reserv():
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="Хорошо", callback_data="reserve_budget")
    )
    builder.adjust(1)
    return builder.as_markup()
