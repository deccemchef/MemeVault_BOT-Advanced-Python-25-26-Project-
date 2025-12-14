from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from constants import text_start, text_help, text_no_fav
import models.keyboards as kb
from models.requests import memes_start, memes_get_query
from aiogram.fsm.context import FSMContext

import data_base.requests as rq

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    await rq.ensure_user_exists(tg_id, username)

    await message.answer(text_start, reply_markup=kb.main)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(text_help)


@router.message(Command('favourites'))
async def cmd_favourites(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    # await rq.ensure_user_exists(tg_id, username)

    favourites = await rq.db_get_user_favourites(tg_id)

    if not favourites:
        await message.answer(text_no_fav)
        return

    for fav in favourites:
        file_id = fav.get("file_id")
        caption = fav.get("caption") or "Из избранного"

        await message.answer_photo(
            photo=file_id,
            caption=caption
        )


@router.message(F.text == 'Помощь')
async def btn_help_keyboard(message: Message):
    await cmd_help(message)


@router.message(F.text == 'Найти мем')
async def btn_find_meme(message: Message, state: FSMContext):
    await memes_start(message, state)


@router.message(F.text == 'Избранное')
async def btn_fav_keyboard(message: Message):
    await cmd_favourites(message)


@router.message(Command('cancel'))
@router.message(F.text == 'Назад')
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Действие отменено.Вы вернулись в главное меню:",
        reply_markup=kb.main
    )

@router.callback_query(F.data == 'new_query')
async def find_new_meme_attempt_callback(callback: CallbackQuery, state: FSMContext):
    await memes_start(callback.message, state)
    await callback.answer()
