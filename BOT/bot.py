import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

# Создаём экземпляры бота и диспетчера
bot = Bot(token='8422146276:AAE7uckmXcNnnTCEbSS_oWl06xJXHZy748g')
dp = Dispatcher()


@dp.message()
async def cmd_start(message: Message):
    await message.answer("Привет!")
    await message.reply("Как дела?")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключён")
