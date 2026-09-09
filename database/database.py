from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, DateTime, func, desc, extract, delete, update
from database.tables import *
from categories import *

engine = None


def init_database():
    global engine
    engine = create_engine("sqlite:///database/database.db", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        if session.scalar(select(Status)):
            return

        stats = [Status(type="Списание"), Status(type="Пополнение"), Status(type="Стартовый капитал")]
        session.add_all(stats)
        session.commit()

        categories = []
        for cat_name in CATEGORIES_KEYWORDS:
            categories.append(Category(name=cat_name))
        categories.append(Category(name=NEW_BALANCE_CATEGORY))
        categories.append(Category(name=DEFAULT_CATEGORY))

        session.add_all(categories)
        session.commit()

    print("База данных успешно инициализирована!")


def example_seed_data():
    global engine
    if not engine:
        raise ValueError("Не инициализирована база данных")

    with Session(engine) as session:
        if session.scalar(select(Users)):
            return

        users = [
            Users(username="dxd", name="Илья", second_name="Сысоев", created_at=datetime(2026, 5, 12, 12, 0)),
            Users(username="rem", name="Даша", second_name="Румянцева", created_at=datetime(2026, 9, 22, 12, 0)),
            Users(username="dima", name="Дима", second_name="Антонов", created_at=datetime(2023, 5, 2, 3, 0)),

        ]

        session.add_all(users)
        session.commit()
        print("Данные успешно внесены")


def example_query():
    global engine
    with Session(engine) as session:
        print("=== 1. Все пользователи ===")
        query = select(Users)
        users = session.scalars(query).all()

        for user in users:
            print(f"chat_id: {user.chat_id} | username: {user.username} | second_name: {user.second_name}")
        print()


        print("=== 2. Фильтрация по дате ===")
        target_date = date(2026, 4, 1)
        query_by_date = select(Users).where(func.date(Users.created_at) <= str(target_date))
        users = session.scalars(query_by_date).all()

        for user in users:
            print(f"Найден: {user.name}")
        print()


        print("=== 3. Выборка отдельных колонок ===")
        query = select(Users.username, Users.created_at)
        res = session.execute(query).all()
        print(res)


        for username, created_at in res:
            print(f"Кто: {username} {created_at}")
        print()


init_database()
# example_seed_data()
# example_query()


# Работа с финансами

def add_income(chat_id, value = 0, desc = None, date = datetime.now(), status_id = 2, cat = None):
    global engine
    with Session(engine) as session:
        new_action = Actions(chat_id=chat_id, status_id=status_id, value=value, desc=desc, date=date, category_id=cat)
        session.add(new_action)
        session.commit()



def add_expenses(chat_id, value = 0, desc = None, date = datetime.now(), cat = None):
    global engine
    with Session(engine) as session:
        new_action = Actions(chat_id=chat_id, status_id=1, value=value, desc=desc, date=date, category_id=cat)
        session.add(new_action)
        session.commit()


def get_balance(chat_id, year, month):
    global engine
    with Session(engine) as session:
        query = select(MountlySummary).where(MountlySummary.chat_id == chat_id , MountlySummary.year == int(year) , MountlySummary.month == int(month))
        result = session.scalar(query)
        return result.end_balance


def update_month_notes(chat_id, type_act, value):
        _, month, year,  = str(datetime.today().strftime("%d.%m.%Y")).split(".")
        global engine
        with Session(engine) as session:
            mon_sum_note = session.query(MountlySummary).filter(MountlySummary.chat_id == chat_id , MountlySummary.year == int(year) , MountlySummary.month == int(month)).first()

            if type_act:
                mon_sum_note.total_income = mon_sum_note.total_income + value
                mon_sum_note.end_balance = mon_sum_note.end_balance + value

            else:
                mon_sum_note.total_expense = mon_sum_note.total_expense - value
                mon_sum_note.end_balance = mon_sum_note.end_balance - value

            session.commit()
            return mon_sum_note.end_balance


def get_analytic_month_db(chat_id, year, month):
    global engine
    with Session(engine) as session:
        mon_sum_note = session.query(MountlySummary).filter(MountlySummary.chat_id == chat_id , MountlySummary.year == int(year) , MountlySummary.month == int(month)).first()
        total_income, total_expense, start_balance, end_balance = mon_sum_note.total_income, mon_sum_note.total_expense, mon_sum_note.start_balance, mon_sum_note.end_balance
        session.commit()
        return total_income, total_expense, start_balance, end_balance


def get_all_checks(chat_id, month, year):
    global engine

    with Session(engine) as session:
        query = (select(Actions).where(Actions.chat_id == chat_id, extract("year", Actions.date) == year, extract("month", Actions.date) == month).order_by(Actions.date))
        checks = session.scalars(query).all()

        acts = []
        for chk in checks:
            acts.append((chk.status_id, chk.value, chk.category_id, chk.date, chk.desc, chk.id))

        return acts


def get_one_check(check_id):
    global engine
    
    with Session(engine) as session:
        query = (select(Actions).where(Actions.id == check_id))
        chk = session.scalars(query).first()

        acts = []
        acts.append((chk.status_id, chk.value, chk.category_id, chk.date, chk.desc, chk.id))

        return acts

# Работа с пользователем

def authentication(chat_id):
    global engine
    with Session(engine) as session:
        if session.scalar(select(Users).where(Users.chat_id == chat_id)):
            return True
        return False


def registration(chat_id, username, name, second_name):
    global engine
    try:
        with Session(engine) as session:
            new_user = Users(chat_id=chat_id, username=username, name=name, second_name=second_name, created_at = datetime.now())
            session.add(new_user)
            session.commit()
            return new_user.chat_id
    except Exception as e:
        print(e)
        return False


def get_users():
    global engine
    with Session(engine) as session:
        query = (select(Users.chat_id))
        res = session.execute(query).all()

        users = []
        for i in res:
            users.append((i.chat_id))

        return users



# Проверка месячной истории

def check_mountly_sum(chat_id):
    global engine
    with Session(engine) as session:
        if session.scalar(MountlySummary).where(MountlySummary.chat_id == chat_id): # Сначала при сообщении проверяем есть ли текущий месяц в бл, если нет, то проверяем есть ли вообзе месяцы у пользователя, если есть, то берем баланс последнего и создаем новый
            return True
        return False


def check_mountly_sum_this_month(chat_id):
    global engine
    _, month, year,  = str(datetime.today().strftime("%d.%m.%Y")).split(".")
    with Session(engine) as session:
        if session.scalar(select(MountlySummary).where(MountlySummary.chat_id == int(chat_id) , MountlySummary.year == int(year) , MountlySummary.month == int(month))):
            return True
        return False


def get_last_month_user(chat_id):
    global engine
    with Session(engine) as session:
        query = (select(MountlySummary).where(MountlySummary.chat_id == chat_id).order_by(desc(MountlySummary.year),desc(MountlySummary.month)).limit(1))
        mon_sum_note = session.scalar(query)
        total_income, total_expense, start_balance, end_balance = mon_sum_note.total_income, mon_sum_note.total_expense, mon_sum_note.start_balance, mon_sum_note.end_balance
        return total_income, total_expense, start_balance, end_balance


def create_mountly_sum(chat_id, value):
    global engine
    try:
        with Session(engine) as session:
            date = str(datetime.today().strftime("%d.%m.%Y")).split(".")
            day, month, year = date

            new_month_sum = MountlySummary(
                chat_id=chat_id, 
                year=int(year), month=int(month),
                start_balance=value,
                end_balance=value
            )

            session.add(new_month_sum)
            session.commit()
            return True
    except Exception as e:
        return False


def get_category_id(cat_name):
    global engine

    with Session(engine) as session:
        category = session.query(Category).filter_by(name=cat_name).first()

        return category.id

def get_category_of_id(cat_id):
    global engine

    with Session(engine) as session:
        category = session.query(Category).filter_by(id=cat_id).first()

        return category.name


def get_top_expense_cat(chat_id):
    global engine

    with Session(engine) as session:
        cats = (select(Category.name, func.sum(Actions.value).label("total_sum")).select_from(Actions).join(Category, Actions.category_id == Category.id).where(Actions.chat_id == chat_id, Actions.status_id == 0).group_by(Category.name).order_by(desc("total_sum")))
        res = session.execute(cats).all()

        return res


def create_reserve_budget(chat_id, category_id, amount, start_date, end_date):
    global engine

    if amount <= 0:
        raise ValueError("Сумма резерва должна быть больше нуля")

    if end_date < start_date:
        raise ValueError("Дата окончания не может быть раньше даты начала")

    with Session(engine) as session:
        reserv = ReservetBudget(chat_id=chat_id, category_id=category_id, amount=amount, start_date=start_date, end_date=end_date)
        session.add(reserv)
        session.commit()


def get_reserve_budget(chat_id, reserve_id):
    global engine

    with Session(engine) as session:
        reserv = (select(ReservetBudget.amount,
                ReservetBudget.category_id,
                ReservetBudget.start_date,
                ReservetBudget.end_date,
                Category.name,
                ReservetBudget.id,).join(Category, ReservetBudget.category_id == Category.id).where(ReservetBudget.chat_id == chat_id, ReservetBudget.id == reserve_id))
        res = session.execute(reserv).first()

        return (res.amount, res.category_id, res.start_date, res.end_date, res.name, res.id)
    

def get_all_reserve_budget(chat_id):
    global engine
    
    with Session(engine) as session:
        query = (
            select(
                ReservetBudget.amount,
                ReservetBudget.category_id,
                ReservetBudget.start_date,
                ReservetBudget.end_date,
                Category.name,
                ReservetBudget.id).join(Category, ReservetBudget.category_id == Category.id).where(ReservetBudget.chat_id == chat_id))
        results = session.execute(query).all()

        reservs = []
        for res in results:
            reservs.append((res.amount, res.category_id, res.start_date, res.end_date, res.name, res.id))

        return reservs

def get_checks_for_period_of_categories(chat_id, category_id, start_date, end_date):
    global engine

    with Session(engine) as session:
        query = (select(Actions.status_id,
                        Actions.category_id,
                        Actions.chat_id,
                        Actions.date,
                        Actions.desc,
                        Actions.value,
                        Actions.id).where(Actions.chat_id == chat_id, 
                                       Actions.category_id == category_id,
                                        Actions.status_id == 1, 
                                        Actions.date >= start_date,
                                        Actions.date < end_date,
                                        ).order_by(Actions.date))
        checks = session.execute(query).all()

        orders = []
        for chk in checks:
            orders.append((chk.status_id, chk.value, chk.category_id, chk.date, chk.desc, chk.id))

        return orders


def get_all_amount_reservs_of_chat_id(chat_id):
     global engine
     with Session(engine) as session:
        query = (select(func.coalesce(func.sum(ReservetBudget.amount),0)).where(ReservetBudget.chat_id == chat_id))

        return session.scalar(query)


def delete_reserve_by_id(chat_id, res_id):
    global engine
    with Session(engine) as session:
        query = (delete(ReservetBudget).where(ReservetBudget.chat_id == chat_id,ReservetBudget.id == res_id))

        result = session.execute(query)
        session.commit()


def chenge_end_date_reserve_by_id(chat_id, res_id, end_date):
    global engine
    with Session(engine) as session:
        query = (update(ReservetBudget).where(ReservetBudget.chat_id == chat_id,ReservetBudget.id == res_id).values(end_date=end_date))

        result = session.execute(query)
        session.commit()


def increase_reserve_amount(chat_id, reserve_id, add_amount):
    global engine

    with Session(engine) as session:
        query = (
            update(ReservetBudget)
            .where(
                ReservetBudget.chat_id == chat_id,
                ReservetBudget.id == reserve_id
            )
            .values(
                amount=ReservetBudget.amount + add_amount
            )
        )

        result = session.execute(query)
        session.commit()

        return result.rowcount > 0