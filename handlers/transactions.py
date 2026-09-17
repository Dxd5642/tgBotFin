from aiogram import Router 

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from buttons.transactions import *
from buttons.main_menu import *

from database import database

from services.transactions.create import handler_just_message
from services.transactions.parser import parse_transaction_message
from schemas.create_order import AgreeCreateCheck
from schemas.registration import Registr

router = Router()


@router.message()
async def main_func(message: Message, state: FSMContext):
    if database.authentication(int(message.chat.id)):
            try:
                type_order, value, desc, date, chat_id, cat = parse_transaction_message(message)
                await message.answer(f"📥 Новая транзакция\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n📚 Автоматически выбранная категория: \n{cat}\n\n📌 Всё указано верно?", reply_markup=get_btn_for_create_check())
                await state.set_state(AgreeCreateCheck.waiting_action)
                await state.update_data(type_order = type_order, value = value, desc = desc, date = date, chat_id = chat_id, cat = cat)

            except Exception as e:
                mes = "😭 Произошло ошибка на сервее, пожалуйста попробуйте позже!"
                await message.answer(mes) #
    else:
        await message.answer("Добро пожаловать в бота для отслеживания своих доходов и расходов!\nПеред началом использования бота, вам необхлдимо написаит ваш изначальный баланс")
        await state.set_state(Registr.waiting_balance)

    

@router.callback_query(F.data.startswith("create_check_true"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    type_order, value, desc, date, chat_id, cat = data.get("type_order"), data.get("value"), data.get("desc"), data.get("date"), data.get("chat_id"), data.get("cat")
    await state.clear()
    await callback.message.edit_text(handler_just_message((type_order, value, desc, date, chat_id, cat)), parse_mode="HTML", reply_markup=get_btn_menu())
    await callback.answer()



@router.callback_query(F.data.startswith("create_check_false"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Создание чека отменено!", reply_markup=get_btn_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("create_check_edit"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgreeCreateCheck.action_edit)
    await callback.message.edit_text("✏️ Введите корректные данные по форме:\n\n{Сумма} {описание} {дата}")
    await callback.answer()


@router.callback_query(F.data.startswith("create_check_category_edit"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgreeCreateCheck.action_edit_category)
    data = await state.get_data()
    type_order, value, desc, date, chat_id, cat = data.get("type_order"), data.get("value"), data.get("desc"), data.get("date"), data.get("chat_id"), data.get("cat")
    await callback.message.edit_text(f"📥 Выбор категории для новой транзакции\nИмеющиеся данные:\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n⬇️Выберите категорию из предложенных ниже:⬇️", reply_markup=get_btn_for_edit_cat())
    await callback.answer()


@router.callback_query(F.data.startswith("create_check_cat_edit_"))
async def callback_sometging(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgreeCreateCheck.waiting_action)
    data = await state.get_data()
    type_order, value, desc, date, chat_id, cat = data.get("type_order"), data.get("value"), data.get("desc"), data.get("date"), data.get("chat_id"), data.get("cat")
    cat = database.get_category_of_id(int(callback.data.split("_")[-1]))
    await state.update_data(cat = cat)
    await callback.message.edit_text(f"📥 Новая транзакция\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n📚 Выбранная категория: \n{cat}\n\n📌 Всё указано верно?", reply_markup=get_btn_for_create_check())
    await callback.answer()


@router.message(AgreeCreateCheck.action_edit)
async def callback_reg(message: Message, state: FSMContext):
    try:
        type_order, value, desc, date, chat_id, cat = parse_transaction_message(message)
        await message.answer(f"📥 Новая транзакция\n\n├ 📅 Дата: {date}\n├ 📝 Описание: {desc}\n├ {'🔴 Тип: Расход' if not type_order else '🟢 Тип: Доход'}\n└ 💰 Сумма: {value} ₽\n\n📚 Автоматически выбранная категория: \n{cat}\n\n📌 Всё указано верно?", reply_markup=get_btn_for_create_check())
        await state.set_state(AgreeCreateCheck.waiting_action)
        await state.update_data(type_order = type_order, value = value, desc = desc, date = date, chat_id = chat_id, cat = cat)
    except:
        await message.answer("Вы не ввели данные не в правильном фармате!\n\nПожалуйста, введите данные в формате:\n{Сумма} {Описание} {Дата}")
    