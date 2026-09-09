import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(str(BASE_DIR / ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")


from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BotCommand, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from btns import *
from database import database
from services import reg_user, handler_just_message, handler_just_message_get_all_value, get_analytic_month, get_balance_user, get_analytic_month, get_info_order, get_all_reserve, is_valid_date, parse_date, create_reserve, get_reserved_budget_of_cat, on_startup, check_balance_and_amount_for_create_reserv, delete_reserv_by_chat_id_and_id, change_date_reserv, adding_amount_for_reserve_budget
from states import Registr, AgreeCreateCheck, CreateReserveBudget, DeketeReserveBudget, ChangeDateReserveBudget, AddingAmountReserveBudget
from generate_excel import generate_excel_report



bot = Bot(token=str(BOT_TOKEN))
db = Dispatcher()


user_view_order_state = {}


async def set_main_commands(bot: Bot):
    main_commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/menu", description="Открыть меню"),
    ]
    await bot.set_my_commands(main_commands)


db.startup.register(on_startup)


@db.message(Command("start", "menu"))
async def menu_func(message: Message, state: FSMContext):
    if database.authentication(int(message.chat.id)):
        await message.answer("🧰 Главное меню: \nВыберите следующее действие:", reply_markup=get_btn_menu())
    else:
        await message.answer("👋 Добро пожаловать в бота для отслеживания своих доходов и расходов!\n\n❗ Перед началом использования бота, вам необходимо написать ваш изначальный баланс: ")
        await state.set_state(Registr.waiting_balance)


@db.message(Registr.waiting_balance)
async def callback_reg(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(reg_user(message))



@db.callback_query(F.data.startswith("analytic_month"))
async def callback_sometging(callback: CallbackQuery):
    message, chart_buffer = get_analytic_month(callback.from_user.id)

    photo_file = BufferedInputFile(chart_buffer.getvalue(), filename="balance_chart.png")
    await callback.message.delete()
    await callback.message.answer_photo(caption=message, reply_markup=get_btn_back(), parse_mode="HTML", photo = photo_file)
    await callback.answer()


@db.callback_query(F.data.startswith("my_balance"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text(get_balance_user(callback.from_user.id), reply_markup=get_btn_back())
    await callback.answer()


@db.callback_query(F.data.startswith("report_order"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text("📊 Формирую ваш отчет, подождите...")

    excel_file = generate_excel_report(callback.from_user.id)

    await callback.message.edit_text("👍 Ваш отчет успешно сформирован!")
    await callback.message.answer_document(document=excel_file,
    caption="Ваша полная выписка расходов и доходов в формате Excel 📑")
    await callback.message.answer("🧰 Главное меню: \nВыберите следующее действие:", reply_markup=get_btn_menu())



@db.callback_query(F.data.startswith("last_checks"))
async def callback_sometging(callback: CallbackQuery):
    markup = get_orders_of_month(callback.message.chat.id, 0)
    await callback.message.edit_text("⬇️⬇️⬇️ Выберите чек ⬇️⬇️⬇️", reply_markup=markup)
    await callback.answer()


@db.callback_query(F.data.startswith("orders_page_"))
async def callback_sometging(callback: CallbackQuery):
    current_page = int(callback.data.replace("orders_page_", ""))
    markup = get_orders_of_month(callback.message.chat.id, current_page)
    await callback.message.edit_text("⬇️⬇️⬇️ Выберите чек ⬇️⬇️⬇️", reply_markup=markup)
    await callback.answer()

@db.callback_query(F.data.startswith("view_desc_order_"))
async def callback_sometging(callback: CallbackQuery):
    order_id, current_page = callback.data.replace("view_desc_order_", "").split("_page_")
    order = get_info_order(order_id)
    await callback.message.edit_text(text=order, reply_markup=get_orders_back(current_page))
    await callback.answer()



@db.callback_query(F.data.startswith("back"))
async def callback_sometging(callback: CallbackQuery):
    msg = callback.message
    text = "Главное меню: \nВыберите следующее действие"

    if msg.photo:
        await msg.delete()
        await msg.answer(text=text, reply_markup=get_btn_menu())

    else:
        await msg.edit_text(text=text, reply_markup=get_btn_menu())
    
    await callback.answer()


# ========== Создание резерва ===========


@db.callback_query(F.data.startswith("reserve_budget"))
async def callback_open_reserve_budget(callback: CallbackQuery):
    text, resevs = get_all_reserve(callback.message.chat.id)

    # Возвращение с кнопочками get_reserve_menu 
    await callback.message.edit_text(text=text, reply_markup=get_reserve_menu(resevs))
    await callback.answer()


@db.callback_query(F.data.startswith("get_reserve_by_id_"))
async def callback_open_reserve_budget(callback: CallbackQuery):
    res_id = int(callback.data.split("_")[-1])

    text = get_reserved_budget_of_cat(callback.message.chat.id, res_id)

    # Возвращение с кнопочками get_reserve_menu 
    await callback.message.edit_text(text=text, reply_markup=get_btn_for_choised_reserve(res_id))
    await callback.answer()


@db.callback_query(F.data.startswith("create_new_reserve"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateReserveBudget.waiting_cat)

    available_balance = check_balance_and_amount_for_create_reserv(callback.message.chat.id)

    await callback.message.edit_text(text=f"❗ Обращаем ваше внимение, что вы можете создать резервный счет на сумму не более: {available_balance} ❗\n\n⬇️ Выберите категорию для зарезервированного счета ⬇️", reply_markup=get_cat_for_create_reserve())
    await callback.answer()


@db.callback_query(F.data.startswith("create_reserve_choise_cat_cancel"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(text="Создание зарезервированного счета отменено 😥", reply_markup=get_btn_back())
    await callback.answer()

@db.callback_query(F.data.startswith("create_reserve_choise_cat_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateReserveBudget.waiting_balance)
    await state.update_data(cat_id = int(callback.data.split("_")[-1]))
    await state.update_data(cat = database.get_category_of_id(int(callback.data.split("_")[-1])))

    await callback.message.edit_text(text="💵 Теперь введите сумму, которую вы хотели бы отложить на зарезервированный счет:", reply_markup=get_cancel_btn_reserve())
    await callback.answer()

@db.message(CreateReserveBudget.waiting_balance)
async def callback_open_reserve_budget(message: Message, state: FSMContext):
    balance = message.text
    try:
        balance = float(balance)
        if check_balance_and_amount_for_create_reserv(message.chat.id) >= balance:
            await state.update_data(balance = balance)
            await message.answer(text="📆 Введите сроки вашего зарезервированного счета 📆\n\nОтправьте сообщение вида: 01.01.26-01.02.26", reply_markup=get_cancel_btn_reserve())
            await state.set_state(CreateReserveBudget.waiting_date)
        else:
            await message.answer(text=f"❗ Вы не можете создать зарезервированный счет больше достпной суммы ❗\n\nВведите сумму в пределах {check_balance_and_amount_for_create_reserv(message.chat.id)} руб.", reply_markup=get_cancel_btn_reserve())
    except:
        await message.answer(text="❗ Введен неправильная сумма!❗\n\nВведите сумму в виде: 600 600.0", reply_markup=get_cancel_btn_reserve())
        

        

@db.message(CreateReserveBudget.waiting_date)
async def callback_open_reserve_budget(message: Message, state: FSMContext):
    dates = str(message.text).replace(" ", "").split("-")
    if is_valid_date(dates[0]) and is_valid_date(dates[1]):
        date1 = parse_date(dates[0])
        await state.update_data(start_date = date1)
        date2 = parse_date(dates[1])
        await state.update_data(end_date = date2)
        data = await state.get_data()
        await message.answer(text=f"Проверьте введенные данные для создания зарезервированного счета:\n\n🚩 Выбранная категория ➡️ {data["cat"]}\n💵 Выделенный баланс ➡️ {data["balance"]}\n📆 Сроки ➡️ {data["start_date"]} - {data["end_date"]}\n\nВсе верно?", reply_markup=get_agree_btns_create_reserve())

    else:
        await message.answer(text="❗ Введены неправильные даты!❗\n\nОтправьте сообщение вида: 01.01.26-01.02.26", reply_markup=get_cancel_btn_reserve())


@db.callback_query(F.data.startswith("create_reserve_true"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = create_reserve(callback.message.chat.id, data['cat_id'], data['balance'], (data["start_date"], data["end_date"]))
    await state.clear()

    await callback.message.edit_text(text="Зарезервированный счет успешно создан!", reply_markup=get_btn_back())
    await callback.answer()

    # сразу выводим инфу через get_reserved_budget_of_cat
    



@db.callback_query(F.data.startswith("create_reserve_false"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    # Тут отменили создание счета

    await callback.message.edit_text(text="Создание зарезервированного счета отменено!", reply_markup=get_btn_back())
    await callback.answer()

@db.callback_query(F.data.startswith("create_reserve_edit"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateReserveBudget.waiting_cat)
    # Тут отменили создание счета

    await callback.message.edit_text(text="⬇️ Выберите категорию для зарезервированного счета ⬇️", reply_markup=get_cat_for_create_reserve())
    await callback.answer()


@db.callback_query(F.data.startswith("reserve_delete_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    # Функция удаления резерва
    res_id = (int(callback.data.split("_")[-1]))
    await state.set_state(DeketeReserveBudget.waiting_action)
    await state.update_data(reserv_id = res_id)

    await callback.message.edit_text(text="😮 Вы уверены, что хотите удалить данный зарезерварованный счет? ", reply_markup=get_btns_delete_action_agree())
    await callback.answer()


@db.callback_query(F.data.startswith("reserve_action_delete_true"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    # Функция удаления резерва
    data = await state.get_data()
    text = delete_reserv_by_chat_id_and_id(callback.message.chat.id, data["reserv_id"])

    await state.clear()
    await callback.message.edit_text(text=text, reply_markup=get_btns_after_delete_reserv())
    await callback.answer()


@db.callback_query(F.data.startswith("reserve_action_delete_false"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = get_reserved_budget_of_cat(callback.message.chat.id, data["reserv_id"])
    await state.clear()

    # Возвращение с кнопочками get_reserve_menu 
    await callback.message.edit_text(text=text, reply_markup=get_btn_for_choised_reserve(data["reserv_id"]))
    await callback.answer()


# Изменение конечной даты
@db.callback_query(F.data.startswith("reserve_change_date_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    res_id = (int(callback.data.split("_")[-1]))
    await state.set_state(ChangeDateReserveBudget.waiting_date)
    await state.update_data(reserv_id = res_id)

    # Возвращение с кнопочками get_reserve_menu 
    await callback.message.edit_text(text="📆 Введите новую дату окончания периода зарезервированного счета 📆\n\nДату необходимо ввести в виде: 01.01.2026", reply_markup=get_btn_cancel_change_date_reserv(res_id))
    await callback.answer()


@db.message(ChangeDateReserveBudget.waiting_date)
async def callback_open_reserve_budget(message: Message, state: FSMContext):
    data = await state.get_data()
    date = str(message.text)
    text = change_date_reserv(message.chat.id, data['reserv_id'], date)
    if text == "Неверная дата":
        await message.answer(text="❗ Введена неправильная дата!❗\n\nОтправьте сообщение вида: 01.01.26 или 01.01.2026", reply_markup=get_btn_cancel_change_date_reserv(data['reserv_id']))
    else:
        await message.answer(text=text, reply_markup=get_btn_retern_after_change_date_reserv(data["reserv_id"]))
        await state.clear()


@db.callback_query(F.data.startswith("cancel_change_date_for_reserve_"))
async def callback_open_reserve_budget(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await message.edit_text(text="❌ Отменено изменение даты в зарезервированном счете", reply_markup=get_btn_retern_after_change_date_reserv(data["reseve_id"]))


# Пополнение счета
@db.callback_query(F.data.startswith("reserve_add_amount_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    res_id = (int(callback.data.split("_")[-1]))
    await state.set_state(AddingAmountReserveBudget.waiting_date)
    await state.update_data(reserv_id = res_id)

    available_balance = check_balance_and_amount_for_create_reserv(callback.message.chat.id)
    
    await callback.message.edit_text(text=f"⬇️ Введите сумму, на которую вы хотите увеличить ваш зав. счет ⬇️\n\n❗ Обращаем ваше ванимание, что вы не можете увеличить зав. счет на сумму более :{available_balance} руб. ❗", reply_markup=get_btn_cancel_change_amount_reserv(res_id))
    await callback.answer()

@db.message(AddingAmountReserveBudget.waiting_date)
async def callback_open_reserve_budget(message: Message, state: FSMContext):
    balance = message.text
    data = await state.get_data()
    try:
        balance = float(balance)
        if check_balance_and_amount_for_create_reserv(message.chat.id) >= balance:

            # Функция пополнения счета
            text = adding_amount_for_reserve_budget(message.chat.id, data['reserv_id'], balance)

            await message.answer(text=text, reply_markup=get_btn_retern_after_change_date_reserv(data['reserv_id']))
            await state.clear()
        else:
            await message.answer(text=f"❗ Вы не можете пополнить зарезервированный счет на сумму больше достпной  ❗\n\nВведите сумму в пределах {check_balance_and_amount_for_create_reserv(message.chat.id)} руб.", reply_markup=get_btn_cancel_change_amount_reserv(data['reserv_id']))
    except:
        await message.answer(text="❗ Введен неправильная сумма!❗\n\nВведите сумму в виде: 600 600.0", reply_markup=get_btn_cancel_change_amount_reserv(data['reserv_id']))
        


@db.callback_query(F.data.startswith("cancel_change_amount_for_reserve_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_text(text="❌ Отменено пополнение зарезервированного счета", reply_markup=get_btn_retern_after_change_date_reserv(data["reserv_id"]))


# =======================================


@db.callback_query(F.data.startswith("create_check_true"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    type_order, value, desc, date, chat_id, cat = data.get("type_order"), data.get("value"), data.get("desc"), data.get("date"), data.get("chat_id"), data.get("cat")
    await state.clear()
    await callback.message.edit_text(handler_just_message((type_order, value, desc, date, chat_id, cat)), parse_mode="HTML", reply_markup=get_btn_menu())
    await callback.answer()



@db.callback_query(F.data.startswith("create_check_false"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Создание чека отменено!", reply_markup=get_btn_menu())
    await callback.answer()


@db.callback_query(F.data.startswith("create_check_edit"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgreeCreateCheck.action_edit)
    await callback.message.edit_text("✏️ Введите корректные данные по форме:\n\n{Сумма} {описание} {дата}")
    await callback.answer()


@db.callback_query(F.data.startswith("create_check_category_edit"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgreeCreateCheck.action_edit_category)
    data = await state.get_data()
    type_order, value, desc, date, chat_id, cat = data.get("type_order"), data.get("value"), data.get("desc"), data.get("date"), data.get("chat_id"), data.get("cat")
    await callback.message.edit_text(f"📥 Выбор категории для новой транзакции\nИмеющиеся данные:\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n⬇️Выберите категорию из предложенных ниже:⬇️", reply_markup=get_btn_for_edit_cat())
    await callback.answer()


@db.callback_query(F.data.startswith("create_check_cat_edit_"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgreeCreateCheck.waiting_action)
    data = await state.get_data()
    type_order, value, desc, date, chat_id, cat = data.get("type_order"), data.get("value"), data.get("desc"), data.get("date"), data.get("chat_id"), data.get("cat")
    cat = database.get_category_of_id(int(callback.data.split("_")[-1]))
    await state.update_data(cat = cat)
    await callback.message.edit_text(f"📥 Новая транзакция\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n📚 Выбранная категория: \n{cat}\n\n📌 Всё указано верно?", reply_markup=get_btn_for_create_check())
    await callback.answer()


@db.message(AgreeCreateCheck.action_edit)
async def callback_reg(message: Message, state: FSMContext):
    try:
        type_order, value, desc, date, chat_id, cat = handler_just_message_get_all_value(message)
        await message.answer(f"📥 Новая транзакция\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n📚 Автоматически выбранная категория: \n{cat}\n\n📌 Всё указано верно?", reply_markup=get_btn_for_create_check())
        await state.set_state(AgreeCreateCheck.waiting_action)
        await state.update_data(type_order = type_order, value = value, desc = desc, date = date, chat_id = chat_id, cat = cat)
    except:
        await message.answer("Вы не ввели данные не в правильном фармате!\n\nПожалуйста, введите данные в формате:\n{Сумма} {Описание} {Дата}")
    

@db.message()
async def main_func(message: Message, state: FSMContext):
    if database.authentication(int(message.chat.id)):
            try:
                type_order, value, desc, date, chat_id, cat = handler_just_message_get_all_value(message)
                await message.answer(f"📥 Новая транзакция\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n📚 Автоматически выбранная категория: \n{cat}\n\n📌 Всё указано верно?", reply_markup=get_btn_for_create_check())
                await state.set_state(AgreeCreateCheck.waiting_action)
                await state.update_data(type_order = type_order, value = value, desc = desc, date = date, chat_id = chat_id, cat = cat)

            except Exception as e:
                mes = "😭 Произошло ошибка на сервее, пожалуйста попробуйте позже!"
                await message.answer(mes) #
    else:
        await message.answer("Добро пожаловать в бота для отслеживания своих доходов и расходов!\nПеред началом использования бота, вам необхлдимо написаит ваш изначальный баланс")
        await state.set_state(Registr.waiting_balance)

    



async def start_bot():
    print("Запуск телеграм-бота...")
    try:
        await set_main_commands(bot)
        await db.start_polling(bot)
    except asyncio.CancelledError:
        print("Ошмбка при запуске!!")
    finally:
        print("Завершение сессии бота...")
        await bot.session.close()
        await db.storage.close()
        print("Телеграм-бот остановлен")


asyncio.run(start_bot())


#TODO переделать картинку при аналитике за месяц, там дата не праивльно
#TODO доделать excel файл, а именно 3 и 4 листы