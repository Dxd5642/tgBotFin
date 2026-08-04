# ПРОБНЫЙ ВАРИАНТ, НЕ ТЕСТИРОВАЛСЯ

import io
import pandas as pd
from datetime import datetime
from aiogram.types import BufferedInputFile
from sqlalchemy.orm import Session
# Импортируй свои модели Check, Action, Status

def generate_excel_report(session: Session, chat_id: int) -> BufferedInputFile:
    """Генерирует Excel файл в памяти и возвращает объект для aiogram"""
    
    # 1. Запрашиваем данные из БД (Join таблиц Check и Action)
    # Замени на свой фактический SQL/ORM запрос!
    records = (
        session.query(
            Action.date,
            Check.value,
            Check.desc,
            Status.name.label("status_name") # Например, 'Доход' / 'Расход'
        )
        .join(Check, Action.check_id == Check.id)
        .join(Status, Action.status_id == Status.id)
        .filter(Action.chat_id == chat_id)
        .order_by(Action.date.desc())
        .all()
    )

    # 2. Преобразуем в список словарей для pandas
    data = []
    for r in records:
        data.append({
            "Дата и время": r.date.strftime("%Y-%m-%d %H:%M"),
            "Тип": r.status_name,
            "Сумма (₽)": r.value,
            "Описание": r.desc
        })

    # Если записей нет, создаем пустой DataFrame с колонками
    df = pd.DataFrame(data if data else [], columns=["Дата и время", "Тип", "Сумма (₽)", "Описание"])

    # 3. Сохраняем Excel в виртуальный файл (в RAM, без использования диска)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Транзакции')
    
    # Возвращаем указатель в начало файла
    output.seek(0)
    
    # Формируем имя файла
    filename = f"report_{datetime.now().strftime('%Y_%m')}.xlsx"
    
    # Возвращаем файл в формате, который понимает aiogram 3
    return BufferedInputFile(output.read(), filename=filename)