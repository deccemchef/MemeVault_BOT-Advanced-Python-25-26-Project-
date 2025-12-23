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
from aiogram.exceptions import TelegramBadRequest

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


@router.callback_query(F.data.startswith("search:fav:"))
async def fav_show_numbers(cb: CallbackQuery, state: FSMContext):
    batch_id = cb.data.split(":")[2]

    data = await state.get_data()
    batches = data.get("batches", {})
    ids = batches.get(batch_id)

    if not ids:
        await cb.answer("Этот альбом слишком старый, контекст потерян 😕", show_alert=True)
        return

    await cb.message.edit_reply_markup(reply_markup=kb.pick_number_kb(len(ids), batch_id))
    await cb.answer()


@router.callback_query(F.data.startswith("search:cancel:"))
async def fav_cancel(cb: CallbackQuery, state: FSMContext):
    batch_id = cb.data.split(":")[2]
    await cb.message.edit_reply_markup(reply_markup=kb.search_controls_kb(batch_id))
    await cb.answer()


@router.callback_query(F.data.startswith("search:add:"))
async def fav_pick_real(cb: CallbackQuery, state: FSMContext):
    _, _, batch_id, idx_str = cb.data.split(":")
    idx = int(idx_str)

    data = await state.get_data()
    batches = data.get("batches", {})
    ids = batches.get(batch_id)

    if not ids or idx < 1 or idx > len(ids):
        await cb.answer("Контекст потерян 😕", show_alert=True)
        return

    meme_id = ids[idx - 1]
    status = await rq.db_add_favourite(cb.from_user.id, meme_id)

    if status == "OK":
        await cb.answer("Добавлено в избранное ✅")
    elif status == "EXISTS":
        await cb.answer("Уже в избранном")
    elif status == "LIMIT":
        await cb.answer("Лимит избранного 10. Удали что-нибудь", show_alert=True)
    else:
        await cb.answer("Пользователь не найден (нужно /start)", show_alert=True)

    # возвращаем обычные кнопки для этого же альбома
    await cb.message.edit_reply_markup(reply_markup=kb.search_controls_kb(batch_id))

@router.callback_query(F.data == "favourites:delete_menu")
async def favourites_delete_menu(cb: CallbackQuery):
    tg_id = cb.from_user.id
    favs = await rq.db_get_favourites(tg_id)

    if not favs:
        await cb.answer("В избранном пусто 😕", show_alert=True)
        return

    meme_ids = [m.meme_id for m in favs[:10]]

    try:
        await cb.message.edit_reply_markup(reply_markup=kb.fav_delete_kb(meme_ids))
    except TelegramBadRequest:
        pass

    await cb.answer()


@router.callback_query(F.data == "favourites:del_cancel")
async def favourites_delete_cancel(cb: CallbackQuery):
    try:
        await cb.message.edit_reply_markup(reply_markup=kb.favourites_manage_kb)
    except TelegramBadRequest:
        pass
    await cb.answer()


@router.callback_query(F.data.startswith("favourites:del:"))
async def favourites_delete_pick(cb: CallbackQuery):
    tg_id = cb.from_user.id
    meme_id = int(cb.data.split(":")[-1])

    status = await rq.db_delete_favourite(tg_id, meme_id)

    if status == "OK":
        await cb.answer("Удалено ✅")
    elif status == "NOTFOUND":
        await cb.answer("Этого мема уже нет в избранном", show_alert=True)
    else:
        await cb.answer("Сначала нажми /start", show_alert=True)
        return

    try:
        await cb.message.edit_reply_markup(reply_markup=kb.favourites_manage_kb)
    except TelegramBadRequest:
        pass


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
        await cb.answer("А все, больше нету 😕", show_alert=True)
        return

    batch_ids = [m.meme_id for m in memes]
    shown_ids = shown_ids + batch_ids

    import secrets
    batch_id = secrets.token_hex(3)

    batches = data.get("batches", {})
    batches[batch_id] = batch_ids

    batch_order = data.get("batch_order", [])
    batch_order.append(batch_id)
    if len(batch_order) > 70:
        old = batch_order.pop(0)
        batches.pop(old, None)

    await state.update_data(shown_ids=shown_ids, batches=batches, batch_order=batch_order)

    media = MediaGroupBuilder()
    for meme in memes:
        if meme.media_type == "photo":
            media.add_photo(media=meme.file_id)
        elif meme.media_type == "gif":
            media.add_animation(media=meme.file_id)
        elif meme.media_type == "video":
            media.add_video(media=meme.file_id)

    await cb.message.answer_media_group(media=media.build())
    await cb.message.answer("Еще мемы 👇", reply_markup=kb.search_controls_kb(batch_id))
    await cb.answer()



@router.callback_query(F.data == "favourites:clear_ask")
async def favourites_clear_ask(cb: CallbackQuery):
    try:
        await cb.message.edit_reply_markup(reply_markup=kb.favourites_clear_confirm_kb)
    except TelegramBadRequest:
        pass
    await cb.answer()


@router.callback_query(F.data == "favourites:clear_cancel")
async def favourites_clear_cancel(cb: CallbackQuery):
    try:
        await cb.message.edit_reply_markup(reply_markup=kb.favourites_manage_kb)
    except TelegramBadRequest:
        pass
    await cb.answer("Отменено")


@router.callback_query(F.data == "favourites:clear_confirm")
async def favourites_clear_confirm(cb: CallbackQuery):
    deleted = await rq.db_clear_favourites(cb.from_user.id)

    if deleted is None:
        await cb.answer("Пользователь не найден", show_alert=True)
        return

    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass

    if deleted == 0:
        await cb.answer("В избранном уже пусто", show_alert=True)
        return

    await cb.answer("Очищено ✅")
    await cb.message.answer(f"Готово! В Избранном больше нет мемов")
