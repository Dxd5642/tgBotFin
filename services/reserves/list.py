from database.database import * 


def get_all_reserve(chat_id):
    reservs = get_all_reserve_budget(chat_id)

    if len(reservs) == 0:
        return "На данный момент список пуст 😥", []

    return "⬇️ Зарезервированные счета: ⬇️", reservs
    
