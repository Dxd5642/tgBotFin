from database.datebase import add_income, add_expenses, registration, create_mountly_sum, get_balance, update_month_notes, get_analytic_month_db, check_mountly_sum_this_month, check_mountly_sum, get_last_month_user
from datetime import datetime
import calendar
import re


def get_name_month(num):
    num = int(num) - 1
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    return months[num]


def handler_just_message_get_all_value(message):
    if not check_mountly_sum_this_month(message.chat.id):
        total_income, total_expense, start_balance, end_balance = get_last_month_user(message.chat.id)
        create_mountly_sum(message.chat.id, end_balance)


    text = str(message.text)
    chat_id = message.chat.id

    date = datetime.today().strftime("%d.%m.%Y")

    pattern3 = r"\d{2}\.\d{2}\.\d{4}"
    pattern2 = r"\d{2}\.\d{2}\.\d{2}"
    pattern1 = r"\d{2}\.\d{2}"

    found_date = None

    if match := re.search(pattern3, text):
        found_date = match.group()
        date = found_date
    elif match := re.search(pattern2, text):
        found_date = match.group()
        date = found_date
    elif match := re.search(pattern1, text):
        found_date = match.group()
        date = f"{found_date}.{datetime.today().year}"

    if found_date:
        text = text.replace(found_date, "")

    text = text.strip()

    if str(date).count(".") == 1: date = f"{date}.{datetime.today().strftime("%Y")}"
    if str(date).count(".") == 2 and len(date) == 8: date[-2] = str(datetime.today().strftime("%Y"))

    flag_space = True
    if " " not in text:
        if not text.replace("+", "").isdigit():
            raise ValueError(f"❌ Не удалось обработать ваше сообщение!\n\n✍️ Введите сумму и описание в виде: \n1500 перевод боссу 04.04")
        else:
            flag_space = False
    elif not text.split(" ")[0].replace("+", "").isdigit():
        raise ValueError("❌ Не удалось обработать ваше сообщение!\n\n✍️ Введите сумму и описание в виде: \n1500 перевод боссу 04.04")


    if "+" in text:
        # Для дохода
        if flag_space:
            text = text.replace(" ", "=-=", 1).split("=-=")
            value = text[0].replace("+", "")
            desc = text[1] or "Прочие доходы"
        else:
            text = text.replace(" ", "=-=", 1).split("=-=")
            value = text[0]
            desc = "Прочие доходы"

        return True, value, desc, date, chat_id


    else:
        # Для расхода
        if flag_space:
            text = text.replace(" ", "=-=", 1).split("=-=")
            value = text[0]
            desc = text[1] or "Прочие расходы"
        else:
            text = text.replace(" ", "=-=", 1).split("=-=")
            value = text[0]
            desc = "Прочие расходы"

        return False, value, desc, date, chat_id


def handler_just_message(message):
    try:
        type_check, value, desc, date, chat_id = None, None, None, None, None
        if isinstance(message, tuple):
            type_check, value, desc, date, chat_id = message
        else:
            type_check, value, desc, date, chat_id = handler_just_message_get_all_value(message) 

        date = datetime.strptime(date, "%d.%m.%Y")
        if type_check:
            add_income(chat_id, value, desc, date)
            balance = update_month_notes(chat_id, True, float(value))
            return f"✅    ✅    ✅    ✅    ✅\n\n🎟️ Создан новый чек на {date}\n\n📈 Доход: {value} руб.\n\n✍️Описание: {desc}\n\n💰 Текущий баланс: {balance}\n\n✅    ✅    ✅    ✅    ✅"
        else:
            add_expenses(chat_id, value, desc, date)
            balance = update_month_notes(chat_id, False, float(value))
            return f"❌    ❌    ❌    ❌    ❌\n\n🎟️ Создан новый чек на {date}\n\n📉 Расход: {value} руб.\n\n✍️ Описание: {desc}\n\n💰 Текущий баланс: {balance} руб.\n\n❌    ❌    ❌    ❌    ❌"

    except Exception as e:
        return str(e)
        return "😭 Произошла ошибка на стороне бота, пожалуйста, поробуйте позже("




def get_balance_user(chat_id):
    date = str(datetime.today().strftime("%d.%m.%Y"))
    balance = get_balance(chat_id, date.split('.')[2], date.split('.')[1])
    return f"⌛ На {date} ваш баланс составляет:\n\n💰 {balance} руб"


def get_analytic_month(chat_id, month = None, year = None):
    if month is None and year is None:
        _, month, year = date = str(datetime.today().strftime("%d.%m.%Y")).split(".")

    total_income, total_expense, start_balance, end_balance = get_analytic_month_db(chat_id, year, month)
    mes = f"📊 Аналитика за месяц:\n\n📅 Отчет за {get_name_month(month)} {year}\n🏦 Баланс в начале месяца: {start_balance}\n💵 Последний баланс: {end_balance}\n🟢 Доходы: {total_income} ₽\n🔴 Расходы: {total_expense} ₽\n💰 Чистый результат: {'+' if total_income + total_expense > 0 else ''}{float(total_income) - abs(float(total_expense))} ₽"
    return mes


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
    if res:
        add_income(chat_id, value, "Первоначальный баланс", status_id=3)
        return "✅ Регистрация прошла успешно!!\n\т😁 Теперь вам доступно главное меню по команде \\menu\n❗ Для добавления расхода просто напишите сумму и описание, для дохода добавьте '+' перед суммой. \n\n👻 Если вы не напишите описание, то будет выбрана категория: \n'Прочие расходы'"

    return "Ошибка регистрации, попробуйте позже!"

