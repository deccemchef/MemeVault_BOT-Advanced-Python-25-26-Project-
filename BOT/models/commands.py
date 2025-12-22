from aiogram import F, Router
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo, InputMediaAnimation, CallbackQuery
from aiogram.filters import CommandStart, Command
from constants import text_start, text_help, text_no_fav
import models.keyboards as kb
from models.requests import memes_start, memes_get_query
from aiogram.fsm.context import FSMContext
from models.requests import db_search_memes_by_tags
from aiogram.types import CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder
from constants import PAGE
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
async def cmd_favourites(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    favourites = await rq.db_get_favourites(tg_id)

    if not favourites:
        await message.answer(text_no_fav)
        return

    favourites = favourites[:10]

    await state.update_data(
        fav_last_ids=[m.meme_id for m in favourites],
        fav_last_count=len(favourites),
    )

    media = []
    for m in favourites:
        if m.media_type == "photo":
            media.append(InputMediaPhoto(media=m.file_id))
        elif m.media_type == "video":
            media.append(InputMediaVideo(media=m.file_id))
        elif m.media_type == "gif":
            media.append(InputMediaAnimation(media=m.file_id))

    if not media:
        await message.answer("В избранном нет таких медиа")
        return

    await message.answer_media_group(media=media)

    await message.answer(
        f"Избранное: {len(media)}/10. Что-то удалить?",
        reply_markup=kb.favourites_manage_kb
    )


@router.message(F.text == 'Помощь')
async def btn_help_keyboard(message: Message):
    await cmd_help(message)


@router.message(F.text == 'Найти мем')
async def btn_find_meme(message: Message, state: FSMContext):
    await memes_start(message, state)


@router.message(F.text == 'Избранное')
async def btn_fav_keyboard(message: Message, state: FSMContext):
    await cmd_favourites(message, state)


@router.message(Command('cancel'))
@router.message(F.text == 'Назад')
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Ты вернулся в главное меню:",
        reply_markup=kb.main
    )


@router.callback_query(F.data == 'new_query')
async def find_new_meme_attempt_callback(callback: CallbackQuery, state: FSMContext):
    await memes_start(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "search:fav")
async def fav_show_numbers(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    n = int(data.get("last_batch_count", 0))

    if n <= 0:
        await cb.answer("Сначала нужно вывести мемы", show_alert=True)
        return

    await cb.message.edit_reply_markup(reply_markup=kb.pick_number_kb(n))
    await cb.answer()


@router.callback_query(F.data == "search:cancel")
async def fav_cancel(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup(reply_markup=kb.search_controls_kb)
    await cb.answer()


@router.callback_query(F.data.startswith("search:add:"))
async def fav_pick_real(cb: CallbackQuery, state: FSMContext):
    idx = int(cb.data.split(":")[-1])

    data = await state.get_data()
    batch_ids = data.get("last_batch_ids", [])

    if not batch_ids or idx < 1 or idx > len(batch_ids):
        await cb.answer("Повтори поиск", show_alert=True)
        return

    meme_id = batch_ids[idx - 1]
    status = await rq.db_add_favourite(cb.from_user.id, meme_id)

    if status == "OK":
        await cb.answer("Добавлено в избранное✅")

    elif status == "EXISTS":
        await cb.answer("Уже в избранном🙌")

    elif status == "LIMIT":
        await cb.answer("Лимит избранного 10. Удали что-нибудь😴", show_alert=True)

    # вообще такой ошибки не должно быть, но на всякий случай
    else:
        await cb.answer("Пользователь не найден, тыкни start", show_alert=True)

    await cb.message.edit_reply_markup(reply_markup=kb.search_controls_kb)


@router.callback_query(F.data == "favourites:delete_menu")
async def favourites_delete_menu(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ids = data.get("fav_last_ids", [])
    n = len(ids)

    if n <= 0:
        await cb.answer("Сначала открой избранное", show_alert=True)
        return

    await cb.message.edit_reply_markup(reply_markup=kb.fav_delete_number_kb(n))
    await cb.answer()


@router.callback_query(F.data == "fav:del_cancel")
async def favourites_delete_cancel(cb: CallbackQuery):
    await cb.message.edit_reply_markup(reply_markup=kb.favourites_manage_kb)
    await cb.answer()


@router.callback_query(F.data.startswith("fav:del:"))
async def favourites_delete_pick(cb: CallbackQuery, state: FSMContext):
    index = int(cb.data.split(":")[-1])

    data = await state.get_data()
    ids = data.get("fav_last_ids", [])

    if not ids or index < 1 or index > len(ids):
        await cb.answer("Открой избранное заново", show_alert=True)
        return

    meme_id = ids[index - 1]
    status = await rq.db_delete_favourite(cb.from_user.id, meme_id)

    if status == "OK":
        await cb.answer("Удалено из избранного ✅")
    elif status == "NOTFOUND":
        await cb.answer("Этого мема уже нет в избранном", show_alert=True)
    else:
        await cb.answer("Пользователь не найден, тыкни start", show_alert=True)

    await cb.message.edit_reply_markup(reply_markup=kb.favourites_manage_kb)


@router.callback_query(F.data == "search:more")
async def search_more(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ngrams = data.get("query_ngrams")
    shown_ids = data.get("shown_ids", [])
    if not ngrams:
        await cb.answer("Сначала введи запрос", show_alert=True)
        return

    memes = await db_search_memes_by_tags(ngrams, limit=PAGE, used_ids=shown_ids)
    if not memes:
        await cb.answer("А все, больше нету😕", show_alert=True)
        return

    package = memes
    batch_ids = [m.meme_id for m in package]
    await state.update_data(
        shown_ids=shown_ids + batch_ids,  # копим те, что уже показали
        last_batch_count=len(package),
        last_batch_ids=batch_ids,
    )

    media = MediaGroupBuilder()
    for meme in package:
        if meme.media_type == "photo":
            media.add_photo(media=meme.file_id)
        elif meme.media_type == "gif":
            media.add_animation(media=meme.file_id)
        elif meme.media_type == "video":
            media.add_video(media=meme.file_id)

    await cb.message.answer_media_group(media=media.build())
    await cb.message.answer("Еще мемчики? 👇", reply_markup=kb.search_controls_kb)
    await cb.answer()
