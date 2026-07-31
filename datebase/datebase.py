from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, DateTime, func
from datebase.tables import *

engine = None


def init_database():
    global engine
    engine = create_engine("sqlite:///datebase/datebase.db", echo=False)
    Base.metadata.create_all(engine)


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