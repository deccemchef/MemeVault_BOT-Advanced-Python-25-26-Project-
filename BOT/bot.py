import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message


from models.commands import router


async def main():
    bot = Bot(token='8422146276:AAE7uckmXcNnnTCEbSS_oWl06xJXHZy748g')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключён")