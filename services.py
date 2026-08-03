from database.datebase import add_income, add_expenses, registration, create_mountly_sum


def handler_just_message(message):
    # Сдесь сначала проверка на месяц
    text = str(message.text)
    if " " not in text: #TODO Обработка просто суммы, без описания
        return "Напишите сумму дохода или расхода и описание к ним!\nНапример: 1400 перевод сестре"

    text = text.replace(" ", "=-=", 1).split("=-=")
    value, desc = text

    if "+" in value:
        # Для дохода
        value = float(value.replace("+", ""))

    else:
        # Для расхода
        pass




def reg_user(message):
    first_name = message.chat.first_name
    second_name = message.chat.last_name
    tg_username = message.chat.username
    chat_id = message.chat.id
    value = message.text

    res = registration(chat_id, tg_username, first_name, second_name)
    if not res:
        return "Ошибка регистрации, попробуйте позже!"

    res = create_mountly_sum(res, value)
    if res:
        return "Регистрация прошла успешно!!\nДалее Теперь вам доступно главное меню по команде '\\menu'\nДля добавления расхода просто напишите сумму и описание, для дохода добавьте '+' перед суммой. Если вы не напишиет описание, то будет выбрана категория: 'Прочие расходы'"

    return "Ошибка регистрации, попробуйте позже!" #TODO Сделать добавление первоначального взноса как отдельный чек

