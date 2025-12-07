from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from constants import text_start, text_help
import models.keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(text_start, reply_markup=kb.main)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(text_help)


@router.message(Command('memes'))
async def cmd_memes(message: Message):
    await message.answer('Введите тэг мема')

@router.message(Command('favourites'))
async def cmd_fav(message: Message):
    await message.answer('Вы зашли в избранное')


@router.message(F.text == 'Помощь')
async def btn_help_keyboard(message: Message):
    await cmd_help(message)


@router.message(F.text == 'Найти мем')
async def btn_find_meme(message: Message):
    await cmd_memes(message)

@router.message(F.text == 'Избранное')
async def btn_fav_keyboard(message: Message):
    await cmd_fav(message)