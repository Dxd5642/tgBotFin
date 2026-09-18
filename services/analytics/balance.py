from database.database import * 
from datetime import datetime

from services.transactions.categories import *
from services.reserves.info import get_reserved_budget_info

from storage.reserve_cache import dict_user_reser_cat


def get_balance_user(chat_id):
    date = str(datetime.today().strftime("%d.%m.%Y"))
    balance = get_balance(chat_id, date.split('.')[2], date.split('.')[1])

    text_cats = ""
    main_balance = balance

    if str(chat_id) in dict_user_reser_cat:
        for reservs in dict_user_reser_cat[str(chat_id)]:
            res_info = get_reserved_budget_info(chat_id, reservs[1])
            main_balance -= float(res_info['amount'])
            text_cats += ("=======================\n\n"
                f"🔒 <b>Лимит по категории «{res_info['cat_name']}»</b>\n"
                f"💵 Остаток: <b>{res_info['remaining']} ₽</b> "
                f"из {res_info['amount']} ₽\n"
            )

    balance_text = f"⌛ Данные на {date} число:\n\n💰 Общий баланс: {balance} руб" + (f"\n💎 Баланс на прочие расходы: {main_balance}\n" + text_cats if text_cats != "" else "")

    return balance_text
