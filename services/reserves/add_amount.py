from database.database import * 

def adding_amount_for_reserve_budget(chat_id, res_id, amount):
    if increase_reserve_amount(chat_id, res_id, amount):
        return f"😊 Ваш зав. счет успешно пополнен на {amount} руб."
    else:
        return "😥 При пополнении счета произошла ошибка!("