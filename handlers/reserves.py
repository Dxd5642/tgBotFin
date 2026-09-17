from aiogram import Router

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from buttons.main_menu import *
from buttons.reserves.menu import *
from buttons.reserves.edit import *
from buttons.reserves.create import *
from buttons.reserves.delete import *

from database import database

from services.reserves.add_amount import *
from services.reserves.change_date import *
from services.reserves.create import *
from services.reserves.delete import *
from services.reserves.info import *
from services.reserves.list import *

from schemas import CreateReserveBudget, DeleteReserveBudget, ChangeDateReserveBudget, AddingAmountReserveBudget


router = Router()


@router.callback_query(F.data.startswith("reserve_budget"))
async def callback_open_reserve_budget(callback: CallbackQuery):
    text, resevs = get_all_reserve(callback.message.chat.id)

    # Возвращение с кнопочками get_reserve_menu 
    await callback.message.edit_text(text=text, reply_markup=get_reserve_menu(resevs))
    await callback.answer()


@router.callback_query(F.data.startswith("get_reserve_by_id_"))
async def callback_open_reserve_budget(callback: CallbackQuery):
    res_id = int(callback.data.split("_")[-1])

    text = get_reserved_budget_of_cat(callback.message.chat.id, res_id)

    # Возвращение с кнопочками get_reserve_menu 
    await callback.message.edit_text(text=text, reply_markup=get_btn_for_choised_reserve(res_id))
    await callback.answer()


@router.callback_query(F.data.startswith("create_new_reserve"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateReserveBudget.waiting_cat)

    available_balance = check_balance_and_amount_for_create_reserv(callback.message.chat.id)

    await callback.message.edit_text(text=f"❗ Обращаем ваше внимение, что вы можете создать резервный счет на сумму не более: {available_balance} ❗\n\n⬇️ Выберите категорию для зарезервированного счета ⬇️", reply_markup=get_cat_for_create_reserve())
    await callback.answer()


@router.callback_query(F.data.startswith("create_reserve_choise_cat_cancel"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(text="Создание зарезервированного счета отменено 😥", reply_markup=get_btn_back())
    await callback.answer()

@router.callback_query(F.data.startswith("create_reserve_choise_cat_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateReserveBudget.waiting_balance)
    await state.update_data(cat_id = int(callback.data.split("_")[-1]))
    await state.update_data(cat = database.get_category_of_id(int(callback.data.split("_")[-1])))

    await callback.message.edit_text(text="💵 Теперь введите сумму, которую вы хотели бы отложить на зарезервированный счет:", reply_markup=get_cancel_btn_reserve())
    await callback.answer()

@router.message(CreateReserveBudget.waiting_balance)
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
        

        

@router.message(CreateReserveBudget.waiting_date)
async def callback_open_reserve_budget(message: Message, state: FSMContext):
    dates = str(message.text).replace(" ", "").split("-")
    if is_valid_date(dates[0]) and is_valid_date(dates[1]):
        date1 = parse_date(dates[0])
        await state.update_data(start_date = date1)
        date2 = parse_date(dates[1])
        await state.update_data(end_date = date2)
        data = await state.get_data()
        await message.answer(text=f"Проверьте введенные данные для создания зарезервированного счета:\n\n🚩 Выбранная категория ➡️ {data['cat']}\n💵 Выделенный баланс ➡️ {data['balance']}\n📆 Сроки ➡️ {data['start_date']} - {data['end_date']}\n\nВсе верно?", reply_markup=get_agree_btns_create_reserve())

    else:
        await message.answer(text="❗ Введены неправильные даты!❗\n\nОтправьте сообщение вида: 01.01.26-01.02.26", reply_markup=get_cancel_btn_reserve())


@router.callback_query(F.data.startswith("create_reserve_true"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = create_reserve(callback.message.chat.id, data['cat_id'], data['balance'], (data["start_date"], data["end_date"]))
    await state.clear()

    await callback.message.edit_text(text="Зарезервированный счет успешно создан!", reply_markup=get_btn_back())
    await callback.answer()



@router.callback_query(F.data.startswith("create_reserve_false"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    # Тут отменили создание счета

    await callback.message.edit_text(text="Создание зарезервированного счета отменено!", reply_markup=get_btn_back())
    await callback.answer()

@router.callback_query(F.data.startswith("create_reserve_edit"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateReserveBudget.waiting_cat)
    # Тут отменили создание счета

    await callback.message.edit_text(text="⬇️ Выберите категорию для зарезервированного счета ⬇️", reply_markup=get_cat_for_create_reserve())
    await callback.answer()


@router.callback_query(F.data.startswith("reserve_delete_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    # Функция удаления резерва
    res_id = (int(callback.data.split("_")[-1]))
    await state.set_state(DeleteReserveBudget.waiting_action)
    await state.update_data(reserv_id = res_id)

    await callback.message.edit_text(text="😮 Вы уверены, что хотите удалить данный зарезерварованный счет? ", reply_markup=get_btns_delete_action_agree())
    await callback.answer()


@router.callback_query(F.data.startswith("reserve_action_delete_true"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    # Функция удаления резерва
    data = await state.get_data()
    text = delete_reserv_by_chat_id_and_id(callback.message.chat.id, data["reserv_id"])

    await state.clear()
    await callback.message.edit_text(text=text, reply_markup=get_btns_after_delete_reserv())
    await callback.answer()


@router.callback_query(F.data.startswith("reserve_action_delete_false"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = get_reserved_budget_of_cat(callback.message.chat.id, data["reserv_id"])
    await state.clear()

    # Возвращение с кнопочками get_reserve_menu 
    await callback.message.edit_text(text=text, reply_markup=get_btn_for_choised_reserve(data["reserv_id"]))
    await callback.answer()


# Изменение конечной даты
@router.callback_query(F.data.startswith("reserve_change_date_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    res_id = (int(callback.data.split("_")[-1]))
    await state.set_state(ChangeDateReserveBudget.waiting_date)
    await state.update_data(reserv_id = res_id)

    # Возвращение с кнопочками get_reserve_menu 
    await callback.message.edit_text(text="📆 Введите новую дату окончания периода зарезервированного счета 📆\n\nДату необходимо ввести в виде: 01.01.2026", reply_markup=get_btn_cancel_change_date_reserv(res_id))
    await callback.answer()


@router.message(ChangeDateReserveBudget.waiting_date)
async def callback_open_reserve_budget(message: Message, state: FSMContext):
    data = await state.get_data()
    date = str(message.text)
    text = change_date_reserv(message.chat.id, data['reserv_id'], date)
    if text == "Неверная дата":
        await message.answer(text="❗ Введена неправильная дата!❗\n\nОтправьте сообщение вида: 01.01.26 или 01.01.2026", reply_markup=get_btn_cancel_change_date_reserv(data['reserv_id']))
    else:
        await message.answer(text=text, reply_markup=get_btn_retern_after_change_date_reserv(data["reserv_id"]))
        await state.clear()


@router.callback_query(F.data.startswith("cancel_change_date_for_reserve_"))
async def callback_open_reserve_budget(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await message.edit_text(text="❌ Отменено изменение даты в зарезервированном счете", reply_markup=get_btn_retern_after_change_date_reserv(data["reseve_id"]))


# Пополнение счета
@router.callback_query(F.data.startswith("reserve_add_amount_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    res_id = (int(callback.data.split("_")[-1]))
    await state.set_state(AddingAmountReserveBudget.waiting_date)
    await state.update_data(reserv_id = res_id)

    available_balance = check_balance_and_amount_for_create_reserv(callback.message.chat.id)
    
    await callback.message.edit_text(text=f"⬇️ Введите сумму, на которую вы хотите увеличить ваш зав. счет ⬇️\n\n❗ Обращаем ваше ванимание, что вы не можете увеличить зав. счет на сумму более :{available_balance} руб. ❗", reply_markup=get_btn_cancel_change_amount_reserv(res_id))
    await callback.answer()

@router.message(AddingAmountReserveBudget.waiting_date)
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
        


@router.callback_query(F.data.startswith("cancel_change_amount_for_reserve_"))
async def callback_open_reserve_budget(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_text(text="❌ Отменено пополнение зарезервированного счета", reply_markup=get_btn_retern_after_change_date_reserv(data["reserv_id"]))

