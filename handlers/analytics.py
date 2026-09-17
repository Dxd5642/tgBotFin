from aiogram import Router

from aiogram import F
from aiogram.types import CallbackQuery, BufferedInputFile

from buttons.main_menu import *

from services.analytics.mountly import get_analytic_month, get_analytic_month
from services.analytics.balance import get_balance_user

from services.generate_excel import generate_excel_report



router = Router()


@router.callback_query(F.data.startswith("analytic_month"))
async def callback_analytic_month(callback: CallbackQuery):
    message, chart_buffer = get_analytic_month(callback.from_user.id)

    photo_file = BufferedInputFile(chart_buffer.getvalue(), filename="balance_chart.png")
    await callback.message.delete()
    await callback.message.answer_photo(caption=message, reply_markup=get_btn_back(), parse_mode="HTML", photo = photo_file)
    await callback.answer()


@router.callback_query(F.data.startswith("my_balance"))
async def callback_my_balance(callback: CallbackQuery):
    await callback.message.edit_text(get_balance_user(callback.from_user.id), parse_mode="HTML", reply_markup=get_btn_back())
    await callback.answer()


@router.callback_query(F.data.startswith("report_order"))
async def callback_report_order(callback: CallbackQuery):
    await callback.message.edit_text("📊 Формирую ваш отчет, подождите...")

    excel_file = generate_excel_report(callback.from_user.id)

    await callback.message.edit_text("👍 Ваш отчет успешно сформирован!")
    await callback.message.answer_document(document=excel_file,
    caption="Ваша полная выписка расходов и доходов в формате Excel 📑")
    await callback.message.answer("🧰 Главное меню: \nВыберите следующее действие:", reply_markup=get_btn_menu())
