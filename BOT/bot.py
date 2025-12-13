import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

from models.commands import router
from models.requests import router as requests_router
from data_base.administrate.tg_chat import router as admin_router

from data_base.models import create_tables


async def main():
    await create_tables()
    bot = Bot(token='8422146276:AAE7uckmXcNnnTCEbSS_oWl06xJXHZy748g')
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(requests_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключён")
