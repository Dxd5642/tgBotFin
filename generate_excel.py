# ПРОБНЫЙ ВАРИАНТ, НЕ ТЕСТИРОВАЛСЯ

import io
import pandas as pd
from datetime import datetime
from aiogram.types import BufferedInputFile
from sqlalchemy.orm import Session
from database import database
from database.tables import *
from sqlalchemy.orm import Session



def generate_excel_report(chat_id: int) -> BufferedInputFile:
    """Генерирует Excel файл в памяти и возвращает объект для aiogram"""
    with Session(database.engine) as session:
        records = (
            session.query(
                Actions.date,
                Actions.value,
                Actions.desc,
            )
            .filter(Actions.chat_id == chat_id)
            .order_by(Actions.date.desc())
            .all()
        )

        data = []
        for r in records:
            data.append({
                "Дата и время": r.date.strftime("%Y-%m-%d %H:%M"),
                "Сумма (₽)": r.value,
                "Описание": r.desc
            })

        # Если записей нет, создаем пустой DataFrame с колонками
        df = pd.DataFrame(data if data else [], columns=["Дата и время", "Сумма (₽)", "Описание"])

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


