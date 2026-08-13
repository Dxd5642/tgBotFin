from database.database import add_income, add_expenses, registration, create_mountly_sum, get_balance, update_month_notes, get_analytic_month_db, check_mountly_sum_this_month, check_mountly_sum, get_last_month_user, get_category_id, get_top_expense_cat
from datetime import datetime
import calendar
import re
from rapidfuzz import process, fuzz
from categories import *

from graphs import graph_simple_analys


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
            cat = detect_category_name(desc)
        else:
            text = text.replace(" ", "=-=", 1).split("=-=")
            value = text[0]
            desc = "Прочие доходы"
            cat = detect_category_name(desc)

        return True, value, desc, date, chat_id, cat


    else:
        # Для расхода
        if flag_space:
            text = text.replace(" ", "=-=", 1).split("=-=")
            value = text[0]
            desc = text[1] or "Прочие расходы"
            cat = detect_category_name(desc)
        else:
            text = text.replace(" ", "=-=", 1).split("=-=")
            value = text[0]
            desc = "Прочие расходы"
            cat = detect_category_name(desc)

        return False, value, desc, date, chat_id, cat


def handler_just_message(message):
    try:
        type_check, value, desc, date, chat_id, cat = None, None, None, None, None, DEFAULT_CATEGORY
        if isinstance(message, tuple):
            type_check, value, desc, date, chat_id, cat = message
        else:
            type_check, value, desc, date, chat_id, cat = handler_just_message_get_all_value(message) 

        date = datetime.strptime(date, "%d.%m.%Y")
        cat_id = get_category_id(cat)
        if type_check:
            add_income(chat_id, value, desc, date, cat=cat_id)
            balance = update_month_notes(chat_id, True, float(value))
            return f"✅    ✅    ✅    ✅    ✅\n\n🎟️ Создан новый чек на {date.strftime("%d.%m.%Y")}\n\n📈 Доход: {value} руб.\n\n✍️Описание: {desc}\n\n📚 Категория: {cat}\n\n💰 Текущий баланс: {balance}\n\n✅    ✅    ✅    ✅    ✅"
        else:
            add_expenses(chat_id, value, desc, date, cat_id)
            balance = update_month_notes(chat_id, False, float(value))
            return f"❌    ❌    ❌    ❌    ❌\n\n🎟️ Создан новый чек на {date.strftime("%d.%m.%Y")}\n\n📉 Расход: {value} руб.\n\n✍️ Описание: {desc}\n\n📚 Категория: {cat}\n\n💰 Текущий баланс: {balance} руб.\n\n❌    ❌    ❌    ❌    ❌"

    except EOFError as e:
        return str(e)
        return "😭 Произошла ошибка на стороне бота, пожалуйста, поробуйте позже("




def get_balance_user(chat_id):
    date = str(datetime.today().strftime("%d.%m.%Y"))
    balance = get_balance(chat_id, date.split('.')[2], date.split('.')[1])
    return f"⌛ На {date} ваш баланс составляет:\n\n💰 {balance} руб"


def get_analytic_month(chat_id, month = None, year = None):
    if month is None and year is None:
        _, month, year = str(datetime.today().strftime("%d.%m.%Y")).split(".")

    total_income, total_expense, start_balance, end_balance = get_analytic_month_db(chat_id, year, month)
    net_result = float(total_income) - abs(float(total_expense))
    now = datetime.now()
    days_in_month = calendar.monthrange(int(year), int(month))[1]
    days_passed = now.day if (now.month == month and now.year == year) else days_in_month
    daily_avg = abs(float(total_expense)) / max(days_passed, 1)

    savings_rate = (net_result / float(total_income) * 100) if float(total_income) > 0 else 0

    status_emoji = "📈" if net_result >= 0 else "📉"
    sign = "+" if net_result > 0 else ""

    top_category_name, top_category_sum = get_top_expense_cat(chat_id)[0]

    mes = (
        f"📊 <b>Аналитика за {get_name_month(month)} {year}</b>\n"
        f"───────────────\n"
        f"🟢 <b>Доходы:</b>  <code>+{total_income:,.2f} ₽</code>\n"
        f"🔴 <b>Расходы:</b> <code>-{abs(float(total_expense)):,.2f} ₽</code>\n"
        f"───────────────\n"
        f"{status_emoji} <b>Итог месяца:</b> <code>{sign}{net_result:,.2f} ₽</code>\n"
        f"💡 <b>Сохранено:</b> <code>{savings_rate:.1f}%</code> от дохода\n\n"
        f"📅 <b>В среднем в день:</b> <code>{float(daily_avg):,.0f} ₽/день</code>\n"
        f"🏆 <b>Главный расход:</b> {top_category_name} (<code>{float(top_category_sum):,.0f} ₽</code>)\n\n"
        f"🏦 <b>Баланс:</b> <code>{float(start_balance):,.0f} ₽</code> ➔ <code>{float(end_balance):,.0f} ₽</code>"
    )

    actions = graph_simple_analys.create_action_list(chat_id, (month, year))
    chart_buffer = graph_simple_analys.generate_balance_chart(start_balance=start_balance, actions=actions)

    return mes, chart_buffer


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



def detect_category_name(desc):
    if not desc:
        return DEFAULT_CATEGORY

    words = desc.lower().split()

    for word in words:
        for cat_name, keywords in CATEGORIES_KEYWORDS.items():
            if word in keywords:
                return cat_name


    for word in word:
        if len(word) < 3:
            continue

        for cat_name, keyword in CATEGORIES_KEYWORDS.items():
            match = process.extractOne(word, keywords, scorer=fuzz.ratio)
            if match and match[1] >= 80:
                return cat_name

    return DEFAULT_CATEGORY