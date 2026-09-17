from database.database import * 
from services.transactions.parser import is_valid_date, parse_date


def change_date_reserv(chat_id, res_id, date):
    if is_valid_date(date):
        date = parse_date(date)
        try:
            chenge_end_date_reserve_by_id(chat_id, res_id, date)
            return "😊 Дата окончания вашего счета успешно изменена!"

        except Exception as e:
            return "😥 При изменении даты окончания вашего зав. счета произошла ошибка("
    else:
        return "Неверная дата"
