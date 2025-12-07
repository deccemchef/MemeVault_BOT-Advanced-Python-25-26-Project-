from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from constants import text_start, text_help

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(text_start)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(text_help)



