from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from buttons.main_menu import *
from database import database
from services.registration.register import reg_user
from schemas.registration import Registr



router = Router()


@router.message(Command("start", "menu"))
async def menu_func(message: Message, state: FSMContext):
    if database.authentication(int(message.chat.id)):
        await message.answer("🧰 Главное меню: \nВыберите следующее действие:", reply_markup=get_btn_menu())
    else:
        await message.answer("👋 Добро пожаловать в бота для отслеживания своих доходов и расходов!\n\n❗ Перед началом использования бота, вам необходимо написать ваш изначальный баланс: ")
        await state.set_state(Registr.waiting_balance)


@router.message(Registr.waiting_balance)
async def callback_reg(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(reg_user(message))