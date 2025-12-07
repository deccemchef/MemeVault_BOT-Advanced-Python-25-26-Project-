from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from constants import text_start, text_help, text_no_fav

router = Router()


def db_get_user(tg_id: int):
    return None


def db_create_user(tg_id: int, username: str | None):
    pass


def db_get_user_favourites(tg_id: int):
    return []


# ее вызываем 2 раза, или в start, или в memes
def ensure_user_exists(tg_id: int, username: str | None):
    user = db_get_user(tg_id)
    if not user:
        db_create_user(tg_id, username)


@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    ensure_user_exists(tg_id, username)

    await message.answer(text_start)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(text_help)


@router.message(Command('favourites'))
async def cmd_favourites(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    ensure_user_exists(tg_id, username)

    favourites = db_get_user_favourites(tg_id)

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
