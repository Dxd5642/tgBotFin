import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(str(BASE_DIR / ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")


from aiogram import Bot, Dispatcher

from handlers.common import set_main_commands
from storage.reserve_cache import on_startup

from handlers.analytics import router as analytics_router
from handlers.common import router as common_router
from handlers.orders import router as orders_router
from handlers.registration import router as registration_router
from handlers.reserves import router as reserves_router
from handlers.transactions import router as transactions_router


bot = Bot(token=str(BOT_TOKEN))
db = Dispatcher()

db.startup.register(on_startup)

db.include_router(analytics_router)
db.include_router(common_router)
db.include_router(orders_router)
db.include_router(registration_router)
db.include_router(reserves_router)
db.include_router(transactions_router)

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
