import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(str(BASE_DIR / ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")


from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from btns import *
from database import datebase
from services import reg_user, handler_just_message, handler_just_message_get_all_value, get_analytic_month, get_balance_user, get_analytic_month
from states import Registr, AgreeCreateCheck
from generate_excel import generate_excel_report



bot = Bot(token=str(BOT_TOKEN))
db = Dispatcher()


async def set_main_commands(bot: Bot):
    main_commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/menu", description="Открыть меню"),
    ]
    await bot.set_my_commands(main_commands)


@db.message(Command("start", "menu"))
async def menu_func(message: Message, state: FSMContext):
    if datebase.authentication(int(message.chat.id)):
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
    await callback.message.edit_text(get_analytic_month(callback.from_user.id), reply_markup=get_btn_back())
    await callback.answer()


@db.callback_query(F.data.startswith("my_balance"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text(get_balance_user(callback.from_user.id), reply_markup=get_btn_back())
    await callback.answer()


@db.callback_query(F.data.startswith("report_order"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text("📊 Формирую ваш отчет, подождите...")

    excel_file = generate_excel_report(callback.from_user.id)

    await callback.message.answer_document(document=excel_file,
    caption="Ваша полная выписка расходов и доходов в формате Excel 📑")


@db.callback_query(F.data.startswith("last_checks"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text("📜 Последние операции:\n\n02.08 — 350 ₽ (кофе) ❌\n02.08 — 1 200 ₽ (продукты) ❌\n01.08 — +15 000 ₽ (фриланс) ❌", reply_markup=get_btn_back())
    await callback.answer()


@db.callback_query(F.data.startswith("settings"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text("""Управление категориями: Добавить/удалить синонимы категорий (например, чтобы слова "такси", "метро", "автобус" автоматически размещались в категорию "Транспорт").

        Валюта: По умолчанию ₽, $, €.

        Напоминания: Настройка ежедневного пуш-уведомления вечером в 21:00 («Не забудь записать сегодняшние расходы!»).""", reply_markup=get_btn_back())
    await callback.answer()



@db.callback_query(F.data.startswith("back"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню: \nВыберите следующее действие", reply_markup=get_btn_menu())
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


@db.message(AgreeCreateCheck.action_edit)
async def callback_reg(message: Message, state: FSMContext):
    try:
        type_order, value, desc, date, chat_id, cat = handler_just_message_get_all_value(message)
        await state.clear()
        await message.answer(handler_just_message((type_order, value, desc, date, chat_id, cat)), reply_markup=get_btn_for_just_message())
        
    except:
        await message.answer("Вы не ввели данные не в правильном фармате!\n\nПожалуйста, введите данные в формате:\n{Сумма} {Описание} {Дата}")
    


@db.message()
async def main_func(message: Message, state: FSMContext):
    if datebase.authentication(int(message.chat.id)):
            try:
                type_order, value, desc, date, chat_id, cat = handler_just_message_get_all_value(message)
                await message.answer(f"📥 Новая транзакция\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ 📚 Категория: {cat}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n📌 Всё указано верно?", reply_markup=get_btn_for_create_check())
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