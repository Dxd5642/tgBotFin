from database.database import * 
from categories import *

from services.transactions.categories import *


def reg_user(message):
    first_name = message.chat.first_name
    second_name = message.chat.last_name
    tg_username = message.chat.username
    chat_id = message.chat.id
    value = message.text

    res = registration(chat_id, tg_username, first_name, second_name)
    if not res:
        return "Ошибка регистрации, попробуйте позже!"

    chat_id = res

    res = create_mountly_sum(res, value)
    cat_id = get_category_id(NEW_BALANCE_CATEGORY)
    if res:
        add_income(chat_id, value, "Первоначальный баланс", status_id=3, cat=cat_id)
        return "✅ Регистрация прошла успешно!!\n\n😁 Теперь вам доступно главное меню по команде \\menu\n\n❗ Для добавления расхода просто напишите сумму и описание, для дохода добавьте '+' перед суммой. \n\n👻 Если вы не напишите описание, то будет выбрана категория: \n'Прочие расходы'"

    return "Ошибка регистрации, попробуйте позже!"

