from aiogram import Router

from aiogram import Bot, F
from aiogram.types import BotCommand, CallbackQuery
from buttons.main_menu import *

router = Router()

async def set_main_commands(bot: Bot):
    main_commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/menu", description="Открыть меню"),
    ]
    await bot.set_my_commands(main_commands)



@router.callback_query(F.data.startswith("back"))
async def callback_sometging(callback: CallbackQuery):
    msg = callback.message
    text = "Главное меню: \nВыберите следующее действие"

    if msg.photo:
        await msg.delete()
        await msg.answer(text=text, reply_markup=get_btn_menu())

    else:
        await msg.edit_text(text=text, reply_markup=get_btn_menu())
    
    await callback.answer()

