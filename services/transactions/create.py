from database.database import * 
from datetime import datetime
from services.transactions.categories import *

from storage.reserve_cache import dict_user_reser_cat
from services.transactions.parser import parse_transaction_message

from services.reserves.info import get_reserved_budget_info



def handler_just_message(message):
    try:
        type_check, value, desc, date, chat_id, cat = None, None, None, None, None, DEFAULT_CATEGORY
        if isinstance(message, tuple):
            type_check, value, desc, date, chat_id, cat = message
        else:
            type_check, value, desc, date, chat_id, cat = parse_transaction_message(message) 

        date = datetime.strptime(date, "%d.%m.%Y")
        cat_id = get_category_id(cat)

        if type_check:
            add_income(chat_id, value, desc, date, cat=cat_id)
            balance = update_month_notes(chat_id, True, float(value))
            return f"✅    ✅    ✅    ✅    ✅\n\n🎟️ Создан новый чек на {date.strftime('%d.%m.%Y')}\n\n📈 Доход: {value} руб.\n\n✍️Описание: {desc}\n\n📚 Категория: {cat}\n\n💰 Текущий баланс: {balance}\n\n✅    ✅    ✅    ✅    ✅"
        else:
            add_expenses(chat_id, value, desc, date, cat_id)
            balance = update_month_notes(chat_id, False, float(value))

            text_res = ""
    
            if str(chat_id) in dict_user_reser_cat:
                for reservs in dict_user_reser_cat[str(chat_id)]:
                    if cat_id == reservs[0]:
                        res_info = get_reserved_budget_info(chat_id, reservs[1])
                        text_res = (
                            "=============================\n\n"
                            f"🔒 <b>Лимит категории «{res_info['cat_name']}»</b>\n\n"
                            f"💵 Остаток: <b>{res_info['remaining']} ₽</b> "
                            f"из {res_info['amount']} ₽\n"
                            f"📆 Дней осталось: <b>{res_info['days_left']}</b>\n\n"

                            f"🎯 <b>Сегодня доступно: "
                            f"{res_info['today_available']} ₽</b>\n"
                            f"🛒 Сегодня потрачено: {res_info['spent_today']} ₽\n"
                            f"📊 Дневная норма: {res_info['daily_limit']} ₽\n\n"

                            f"📅 Период: "
                            f"{res_info['start_date']} — {res_info['end_date']}\n"
                        )

            return f"❌    ❌    ❌    ❌    ❌\n\n🎟️ Создан новый чек на {date.strftime('%d.%m.%Y')}\n\n📉 Расход: {value} руб.\n\n✍️ Описание: {desc}\n\n📚 Категория: {cat}\n\n💰 Текущий баланс: {balance} руб.\n\n{text_res}❌    ❌    ❌    ❌    ❌"

    except EOFError as e:
        return str(e)
        return "😭 Произошла ошибка на стороне бота, пожалуйста, поробуйте позже("

