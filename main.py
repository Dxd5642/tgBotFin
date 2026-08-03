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
from services import reg_user
from states import Registr



bot = Bot(token=str(BOT_TOKEN))
db = Dispatcher()


async def set_main_commands(bot: Bot):
    main_commands = [
        BotCommand(command="/start", description="Запустить / перезапустить бота / открыть меню"),
        BotCommand(command="/menu", description="Открыть меню"),
    ]
    await bot.set_my_commands(main_commands)


@db.message(Command("start", "menu"))
async def menu_func(message: Message, state: FSMContext):
    if datebase.authentication(int(message.chat.id)):
        await message.answer("Главное меню: \nВыберите следующее действие", reply_markup=get_btn_menu())
    else:
        await message.answer("Добро пожаловать в бота для отслеживания своих доходов и расходов!\nПеред началом использования бота, вам необхлдимо написаит ваш изначальный баланс")
        await state.set_state(Registr.waiting_balance)


@db.message(Registr.waiting_balance)
async def callback_reg(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(reg_user(message))



@db.callback_query(F.data.startswith("analytic_month"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text("📊 Аналитика за месяц:\n\n📅 Отчет за Август 2026\n🟢 Доходы: 85 000 ₽\n🔴 Расходы: 42 300 ₽\n💰 Чистый результат: +42 700 ₽", reply_markup=get_btn_back())
    await callback.answer()


@db.callback_query(F.data.startswith("my_balance"))
async def callback_sometging(callback: CallbackQuery):
    await callback.message.edit_text("💳 Мой баланс\n\n💳 Текущий баланс: 124 500 ₽", reply_markup=get_btn_back())
    await callback.answer()


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

@db.message()
async def main_func(message: Message):
    text = str(message.text).replace(" ", "-=-", 1)
    text = text.split("-=-")
    mes = f"✅ {"Расход" if "+" not in text[0] else "Доход"}: {text[0]}₽\n💳 Баланс: 10000₽"
    await message.answer(mes)



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