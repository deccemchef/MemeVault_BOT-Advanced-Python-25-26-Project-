from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.media_group import MediaGroupBuilder

from ..keyboards import *
from ..data_base import *
from ..constants import PAGE

import secrets

router = Router()


class MemeSearchState(StatesGroup):
    waiting_for_query = State()


def generate_ngrams(words):
    ngrams = []
    n = len(words)
    for start in range(n):
        for end in range(start + 1, n + 1):
            ngrams.append(" ".join(words[start:end]))
    return ngrams


@router.message(Command("memes"))
async def memes_start(message: Message, state: FSMContext):
    await message.answer("Введите текст запроса:", reply_markup=kb.search_menu)
    await state.set_state(MemeSearchState.waiting_for_query)


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Нет активного действия. Нечего отменять.")
        return

    await state.clear()
    await message.answer("Действие отменено.")


# вводит текст

@router.message(MemeSearchState.waiting_for_query, F.text)
async def memes_get_query(message: Message, state: FSMContext):
    query = message.text.strip()
    if not query:
        await message.answer("Напиши тег/запрос текстом 🙂", reply_markup=kb.search_menu)
        return

    words = query.split()
    ngrams = [n.lower() for n in generate_ngrams(words)]

    # старые batches забираем, чтобы старые альбомы тоже работали
    data = await state.get_data()
    batches = data.get("batches", {})
    batch_order = data.get("batch_order", [])

    # новый запрос будет хранить все новые айдишники
    shown_ids: list[int] = []

    memes = await rq.db_search_memes_by_tags(ngrams, limit=PAGE, used_ids=shown_ids)

    if not memes:
        await message.answer("😕 Ничего не найдено. Введи другой тег:", reply_markup=kb.search_menu)
        # состояние не сбрасываем - сможет новый тег писать сразу(просил Егор)
        return

    batch_ids = [m.meme_id for m in memes]
    shown_ids = batch_ids.copy()

    # айдишник для этого альбома
    batch_id = secrets.token_hex(3)

    batches[batch_id] = batch_ids
    batch_order.append(batch_id)

    # будем хранить последние 70 альбомов
    if len(batch_order) > 70:
        old = batch_order.pop(0)
        batches.pop(old, None)

    await state.update_data(
        query_ngrams=ngrams,  # еще мемы
        shown_ids=shown_ids,
        batches=batches,  # все альбомы (для избранного по старым, в том числе)
        batch_order=batch_order,
    )

    media = MediaGroupBuilder()
    for meme in memes:
        if meme.media_type == "photo":
            media.add_photo(media=meme.file_id)
        elif meme.media_type == "gif":
            media.add_video(media=meme.file_id)
        elif meme.media_type == "video":
            media.add_video(media=meme.file_id)

    await message.answer_media_group(media=media.build())

    await message.answer(
        "Что-то понравилось? Добавь в избранное или посмотри еще😉",
        reply_markup=kb.search_controls_kb(batch_id),
    )
