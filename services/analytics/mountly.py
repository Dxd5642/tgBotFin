from database.database import * 
from datetime import datetime
import calendar
from categories import *

from services import graph_simple_analys


def get_name_month(num):
    num = int(num) - 1
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    return months[num]


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
