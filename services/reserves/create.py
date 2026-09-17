from database.database import * 
from datetime import datetime

from storage.reserve_cache import dict_user_reser_cat


def create_reserve(chat_id, category_id, amount, dates):
    try:
        create_reserve_budget(chat_id, category_id, amount, dates[0], dates[1])
        cat_list = [(i[1], i[5]) for i in get_all_reserve_budget(chat_id)]
        del dict_user_reser_cat[chat_id]
        dict_user_reser_cat[chat_id] = cat_list
        return "Зарезервированный счет успешно создан!"
    except:
        return "При создании зарезервированного счета произошло ошибка("


def check_balance_for_create_reserv(chat_id, res_bal):
    date = str(datetime.today().strftime("%d.%m.%Y"))
    balance = get_balance(chat_id, date.split('.')[2], date.split('.')[1])

def check_balance_and_amount_for_create_reserv(chat_id):
    date = str(datetime.today().strftime("%d.%m.%Y"))
    balance = get_balance(chat_id, date.split('.')[2], date.split('.')[1])
    amount_all_reservs = get_all_amount_reservs_of_chat_id(chat_id)
    return max(balance - amount_all_reservs, 0.0)
