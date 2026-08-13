import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict

from database.database import get_all_checks


def create_action_list(chat_id, date):
    month, year = date
    checks = get_all_checks(chat_id, month, year)
    
    if not checks:
        return []

    daily_totals = defaultdict(float)

    for act in checks:
        act_type = act[0]   # 0 — расход, 1 — доход
        amount = act[1]     # сумма
        act_date = act[3]   # дата (объект datetime/date)

        if act_type == 0:
            daily_totals[act_date] -= amount
        elif act_type == 1:
            daily_totals[act_date] += amount

    # Преобразуем словарь в нужный формат списка словарей
    actions = [
        {'date': act_date, 'value': day_sum}
        for act_date, day_sum in daily_totals.items()
    ]

    return actions


def generate_balance_chart(start_balance: float, actions: list) -> io.BytesIO: #TODO Переделать тута, а то хуня какая - то

    dates = []
    balances = []

    current_balance = start_balance

        
    if actions:
        first_date = actions[0]['date']
        dates.append(first_date)
        balances.append(start_balance)

    for act in actions:
        current_balance += act['value']
        dates.append(act['date'])
        balances.append(current_balance)

    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    
    ax.plot(dates, balances, color='#2b5c8f', linewidth=2.5, marker='o', markersize=4, label='Баланс')

    ax.fill_between(dates, balances, start_balance, color='#2b5c8f', alpha=0.15)

    ax.axhline(y=start_balance, color='gray', linestyle='--', alpha=0.6, label='Старт месяца')

    # 3. Оформление осей и сетки
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m')) # Формат даты: "07.08"
    fig.autofmt_xdate() # Поворачиваем даты под углом, чтобы не накладывались

    ax.axhline(
        y=start_balance,       
        color='#e74c3c',         
        linestyle='--',         
        linewidth=1.8,          
        alpha=0.9,               
        label='Линия нуля',    
        zorder=3                
    )

    ax.set_title("Динамика баланса за месяц", fontsize=12, fontweight='bold', pad=10)
    ax.set_ylabel("Сумма (₽)", fontsize=10)
    ax.legend(loc="upper left")

    # Убираем лишние рамки сверху и справа
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    # 4. Сохраняем график в буфер памяти (BytesIO) без записи на диск
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig) # Закрываем фигуру, чтобы не забивать оперативку

    return buf