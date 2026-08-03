from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, DateTime, func
from database.tables import *

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

def add_income(chat_id, value = 0, desc = None, date = datetime.now()):
    global engine
    with Session(engine) as session:
        new_check = Checks(value=value, desc=desc)
        session.add(new_check)
        session.commit()

        new_action = Actions(chat_id=chat_id, status_id=1, check_id=new_check.id, date=date)
        session.add(new_action)
        session.commit()


def add_expenses(chat_id, value = 0, desc = None, date = datetime.now()):
    global engine
    with Session(engine) as session:
        new_check = Checks(value=value, desc=desc)
        session.add(new_check)
        session.commit()

        new_action = Actions(chat_id=chat_id, status_id=0, check_id=new_check.id, date=date)
        session.add(new_action)
        session.commit()



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


# Проверка месячной истории

def check_mountly_sum(chat_id):
    global engine
    with Session(engine) as session:
        if session.scalar(MountlySummary).where(MountlySummary.chat_id == chat_id):
            return True
        return False


def create_mountly_sum(chat_id, value):
    global engine
    try:
        with Session(engine) as session:
            date = str(datetime.today().strftime("%d.%m.%Y")).split(".")
            day, month, year = date

            new_month_sum = MountlySummary(
                chat_id=chat_id, 
                year=year, month=month,
                start_balance=value,
                end_balance=0
            )

            session.add(new_month_sum)
            session.commit()
            return True
    except Exception as e:
        return False