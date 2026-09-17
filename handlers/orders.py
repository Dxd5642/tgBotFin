from aiogram import Router

from aiogram import F
from aiogram.types import CallbackQuery

from buttons.orders import *
from services.orders.info import get_info_order



router = Router()

@router.callback_query(F.data.startswith("last_checks"))
async def callback_last_orders(callback: CallbackQuery):
    markup = get_orders_of_month(callback.message.chat.id, 0)
    await callback.message.edit_text("⬇️⬇️⬇️ Выберите чек ⬇️⬇️⬇️", reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("orders_page_"))
async def callback_sometging(callback: CallbackQuery):
    current_page = int(callback.data.replace("orders_page_", ""))
    markup = get_orders_of_month(callback.message.chat.id, current_page)
    await callback.message.edit_text("⬇️⬇️⬇️ Выберите чек ⬇️⬇️⬇️", reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data.startswith("view_desc_order_"))
async def callback_sometging(callback: CallbackQuery):
    order_id, current_page = callback.data.replace("view_desc_order_", "").split("_page_")
    order = get_info_order(order_id)
    await callback.message.edit_text(text=order, reply_markup=get_orders_back(current_page))
    await callback.answer()
