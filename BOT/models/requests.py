from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models import keyboards as kb
from aiogram.utils.media_group import MediaGroupBuilder
from constants import PAGE
from data_base.requests import db_search_memes_by_tags


router = Router()


class MemeSearchState(StatesGroup):
    waiting_for_query = State()


def generate_ngrams(words):
    """
    Принимает список слов и возвращает все возможные фразы
    из подряд идущих слов: все 1-словные, 2-словные, ..., n-словные.
    """
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
    # Проверяем, есть ли состояние
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Нет активного действия. Нечего отменять.")
        return

    # Очищаем состояние
    await state.clear()
    await message.answer("Действие отменено.")


# вводит текст

@router.message(MemeSearchState.waiting_for_query, F.text)
async def memes_get_query(message: Message, state: FSMContext):
    query = message.text.strip()
    words = query.split()

    ngrams = generate_ngrams(words)
    ngrams = [n.lower() for n in ngrams]

    already_shown_ids: list[int] = []

    memes = await db_search_memes_by_tags(ngrams, limit=PAGE, used_ids=already_shown_ids)

    if not memes:
        await message.answer("😕 Ничего не найдено", reply_markup=kb.not_found_menu)
        await state.clear()
        return

    batch = memes
    batch_ids = [m.meme_id for m in batch]

    await state.update_data(
        query_ngrams=ngrams,
        shown_ids=batch_ids.copy(),
        last_batch_count=len(batch),
        last_batch_ids=batch_ids,
    )

    media = MediaGroupBuilder()
    for meme in batch:
        if meme.media_type == "photo":
            media.add_photo(media=meme.file_id)
        elif meme.media_type == "gif":
            media.add_animation(media=meme.file_id)
        elif meme.media_type == "video":
            media.add_video(media=meme.file_id)

    await message.answer_media_group(media=media.build())
    await message.answer(
        "Что-то понравилось? Добавь в избранное или посмотри еще😉",
        reply_markup=kb.search_controls_kb,
    )

