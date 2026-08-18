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
from services import reg_user, handler_just_message, handler_just_message_get_all_value, get_analytic_month, get_balance_user, get_analytic_month, get_info_order
from states import Registr, AgreeCreateCheck
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

@db.callback_query(F.data.startswith("settings"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text("""Управление категориями: Добавить/удалить синонимы категорий (например, чтобы слова "такси", "метро", "автобус" автоматически размещались в категорию "Транспорт").

        Валюта: По умолчанию ₽, $, €.

        Напоминания: Настройка ежедневного пуш-уведомления вечером в 21:00 («Не забудь записать сегодняшние расходы!»).""", reply_markup=get_btn_back())
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


@db.callback_query(F.data.startswith("create_check_true"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    type_order, value, desc, date, chat_id, cat = data.get("type_order"), data.get("value"), data.get("desc"), data.get("date"), data.get("chat_id"), data.get("cat")
    await state.clear()
    await callback.message.edit_text(handler_just_message((type_order, value, desc, date, chat_id, cat)), reply_markup=get_btn_for_just_message())
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
    print("Запуск Телеграм-бота...")
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