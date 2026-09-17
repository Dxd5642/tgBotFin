from database.database import * 
from storage.reserve_cache import dict_user_reser_cat

def delete_reserv_by_chat_id_and_id(chat_id, res_id):
    try:
        delete_reserve_by_id(chat_id, res_id)
        del dict_user_reser_cat[chat_id]
        return "😊 Зарезервированный счет успешно удален!"

    except Exception as e:
        return "😥 При удалении зарезервированного счета произошла ошибка("
