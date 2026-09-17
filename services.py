from database.database import * 
from datetime import datetime, timedelta
import calendar
import re
from rapidfuzz import process, fuzz
from categories import *

from graphs import graph_simple_analys



dict_user_reser_cat = {} # chat_id = ["Категории"]

async def on_startup():
    print("Бот запускается...")
    users = get_users()
    for user in users:
        cats = [(i[1], i[5]) for i in get_all_reserve_budget(user)]
        dict_user_reser_cat[str(user)] = cats

def get_name_month(num):
    num = int(num) - 1
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    return months[num]

def is_valid_date(value: str) -> bool:
    for fmt in ("%d.%m.%y", "%d.%m.%Y"):
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            pass

def parse_date(value: str):
    for fmt in ("%d.%m.%y", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None



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

    main_cat_text = ""
    top_category_name, top_category_sum = get_top_expense_cat(chat_id)[0]
    if top_category_name is None or top_category_sum is None:
        pass
    else:
        main_cat_text = f"🏆 <b>Главный расход:</b> {top_category_name} (<code>{float(top_category_sum):,.0f} ₽</code>)\n\n"

    mes = (
        f"📊 <b>Аналитика за {get_name_month(month)} {year}</b>\n"
        f"───────────────\n"
        f"🟢 <b>Доходы:</b>  <code>+{total_income:,.2f} ₽</code>\n"
        f"🔴 <b>Расходы:</b> <code>-{abs(float(total_expense)):,.2f} ₽</code>\n"
        f"───────────────\n"
        f"{status_emoji} <b>Итог месяца:</b> <code>{sign}{net_result:,.2f} ₽</code>\n"
        f"💡 <b>Сохранено:</b> <code>{savings_rate:.1f}%</code> от дохода\n\n"
        f"📅 <b>В среднем в день:</b> <code>{float(daily_avg):,.0f} ₽/день</code>\n"
        f"{main_cat_text}\n"
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


def get_info_order(order_id):
    order = get_one_check(order_id)[0]

    date = order[3].strftime("%d.%m.%Y %H:%M").split(" ")
    if date[1] != "00:00": date[1] = f"в {date[1]}"
    else: date[1] = ""
    cat = get_category_of_id(order[2])
    text=f"🧾 Информация о чеке от 18.08.2026\n\n📌 Категория: {cat}\n📝 Описание: {order[4]}\n💰 Сумма: {float(order[1]):,.0f} ₽\n📊 Тип: {'🔴 Расход' if order[0] == 0 else '🟢 Доход'}\n📅 Дата: {date[0]} в {date[1]}"

    return text

# === Работа с резервом ===

# Создание резерва: выбор категории и указание лимита
def create_reserve(chat_id, category_id, amount, dates):
    try:
        create_reserve_budget(chat_id, category_id, amount, dates[0], dates[1])
        dict_user_reser_cat[chat_id].append(category_id)
        return "Зарезервированный счет успешно создан!"
    except:
        return "При создании зарезервированного счета произошло ошибка("


# Получение списка резервов
def get_all_reserve(chat_id):
    reservs = get_all_reserve_budget(chat_id)

    if len(reservs) == 0:
        return "На данный момент список пуст 😥", []

    return "⬇️ Зарезервированные счета: ⬇️", reservs
    


def get_reserved_spent(chat_id, start_date, end_date, category_id):
    orders = get_checks_for_period_of_categories(chat_id, category_id, start_date, end_date)

    spent = 0.0

    for i in orders:
        value = i[1]
        spent += float(value)


    return spent
def get_reserved_budget_info(chat_id, reserve_id):
    today = datetime.today().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    reserve = get_reserve_budget(
        chat_id,
        reserve_id
    )

    amount = float(reserve[0])
    start_date = reserve[2]
    end_date = reserve[3]
    category_id = reserve[-1]

    # ---------------------------------------------------------
    # Если резерв ещё не начался
    # ---------------------------------------------------------

    if today < start_date:

        spent = get_reserved_spent(
            chat_id,
            start_date,
            end_date,
            category_id
        )

        remaining = max(
            0.0,
            amount - spent
        )

        days_left = (
            end_date - start_date
        ).days + 1

        current_day_limit = (
            remaining / days_left
            if days_left > 0
            else 0.0
        )

        spent_today = 0.0
        today_available = 0.0

    # ---------------------------------------------------------
    # Если резерв уже закончился
    # ---------------------------------------------------------

    elif today > end_date:

        spent = get_reserved_spent(
            chat_id,
            start_date,
            end_date,
            category_id
        )

        remaining = max(
            0.0,
            amount - spent
        )

        days_left = 0
        current_day_limit = 0.0
        spent_today = 0.0
        today_available = 0.0

    # ---------------------------------------------------------
    # Резерв действует сегодня
    # ---------------------------------------------------------

    else:

        # Все расходы ДО сегодняшнего дня
        spent_before_today = get_reserved_spent(
            chat_id,
            start_date,
            today,
            category_id
        )

        # Расходы ТОЛЬКО сегодня
        spent_today = get_reserved_spent(
            chat_id,
            today,
            today + timedelta(days=1),
            category_id
        )

        # Общие расходы за весь период
        spent = (
            spent_before_today +
            spent_today
        )

        # Остаток бюджета ДО сегодняшних трат
        remaining_before_today = max(
            0.0,
            amount - spent_before_today
        )

        # Остаток бюджета с учётом сегодняшних трат
        remaining = max(
            0.0,
            amount - spent
        )

        # Количество дней, включая сегодняшний
        days_left = (
            end_date - today
        ).days + 1

        # НОРМА НА СЕГОДНЯ
        #
        # ВАЖНО:
        # здесь ещё нет сегодняшнего расхода
        current_day_limit = (
            remaining_before_today / days_left
            if days_left > 0
            else 0.0
        )

        # Сколько можно потратить ЕЩЁ сегодня
        today_available = current_day_limit - spent_today

    return {
        "cat_name": reserve[-2],
        "amount": round(amount, 2),
        "spent": round(spent, 2),
        "remaining": round(remaining, 2),
        "days_left": days_left,
        "daily_limit": round(current_day_limit, 2), #TODO также обновить аналитику за месяц
        "spent_today": round(spent_today, 2),
        "today_available": round(today_available, 2),
        "start_date": start_date.strftime("%d.%m.%y"),
        "end_date": end_date.strftime("%d.%m.%y")
    }

def get_reserved_budget_of_cat(chat_id, reserve_id):
    res_info = get_reserved_budget_info(chat_id, reserve_id)

    return f"🔒 Зарезервированные деньги\n\n{res_info['cat_name']}\n💰 Выделено: {res_info['amount']} ₽\n💸 Потрачено: {res_info['spent']} ₽\n💵 Осталось: {res_info['remaining']} ₽\n\n📅 Период:\n{res_info['start_date']} — {res_info['end_date']} (включительно)\n\n📆 Осталось дней: {res_info['days_left']}\n🎯 Сегодня можно: {res_info['daily_limit']} ₽\n🛒 Потрачено сегодня: {res_info['spent_today']} ₽\n{'✅' if res_info['today_available'] > 0 else '❌'} Осталось на сегодня: {res_info['today_available']} ₽"


def check_balance_for_create_reserv(chat_id, res_bal):
    date = str(datetime.today().strftime("%d.%m.%Y"))
    balance = get_balance(chat_id, date.split('.')[2], date.split('.')[1])


def check_balance_and_amount_for_create_reserv(chat_id):
    date = str(datetime.today().strftime("%d.%m.%Y"))
    balance = get_balance(chat_id, date.split('.')[2], date.split('.')[1])
    amount_all_reservs = get_all_amount_reservs_of_chat_id(chat_id)
    return max(balance - amount_all_reservs, 0.0)


def delete_reserv_by_chat_id_and_id(chat_id, res_id):
    try:
        delete_reserve_by_id(chat_id, res_id)
        return "😊 Зарезервированный счет успешно удален!"

    except Exception as e:
        return "😥 При удалении зарезервированного счета произошла ошибка("


def change_date_reserv(chat_id, res_id, date):
    if is_valid_date(date):
        date = parse_date(date)
        try:
            chenge_end_date_reserve_by_id(chat_id, res_id, date)
            return "😊 Дата окончания вашего счета успешно изменена!"

        except Exception as e:
            return "😥 При изменении даты окончания вашего зав. счета произошла ошибка("
    else:
        return "Неверная дата"


def adding_amount_for_reserve_budget(chat_id, res_id, amount):
    if increase_reserve_amount(chat_id, res_id, amount):
        return f"😊 Ваш зав. счет успешно пополнен на {amount} руб."
    else:
        return "😥 При пополнении счета произошла ошибка!("