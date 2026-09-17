from database.database import * 
from datetime import datetime, timedelta


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

