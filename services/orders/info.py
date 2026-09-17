from database.database import * 


def get_info_order(order_id):
    order = get_one_check(order_id)[0]

    date = order[3].strftime("%d.%m.%Y %H:%M").split(" ")
    if date[1] != "00:00": date[1] = f"в {date[1]}"
    else: date[1] = ""
    cat = get_category_of_id(order[2])
    text=f"🧾 Информация о чеке от 18.08.2026\n\n📌 Категория: {cat}\n📝 Описание: {order[4]}\n💰 Сумма: {float(order[1]):,.0f} ₽\n📊 Тип: {'🔴 Расход' if order[0] == 0 else '🟢 Доход'}\n📅 Дата: {date[0]} в {date[1]}"

    return text