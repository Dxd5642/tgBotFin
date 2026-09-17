from database.database import * 
from datetime import datetime
import re
from services.transactions.categories import *
from rapidfuzz import process, fuzz



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


def parse_transaction_message(message):
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

    if str(date).count(".") == 1: date = f"{date}.{datetime.today().strftime('%Y')}"
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
