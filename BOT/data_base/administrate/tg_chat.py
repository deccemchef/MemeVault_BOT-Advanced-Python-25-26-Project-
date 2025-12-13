"""from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select

from models import async_session, Meme, Tag, MemeTag

router = Router()

ADMIN_CHAT_ID = -1001234567890  # <-- сюда вставь id вашего закрытого чата/канала
ALLOWED_ADMIN_USER_IDS: set[int] = {1223518825, 1331295709}  # опционально: {111, 222}. Если пусто — проверяем только chat_id


def _parse_tags_from_caption(caption: str) -> list[str]:
    parts = [p.strip() for p in caption.split(",")]
    tags = [t for t in parts if t]
    seen = set()
    unique_tags = []
    for t in tags:
        key = t.lower()
        if key not in seen:
            seen.add(key)
            unique_tags.append(t)
    return unique_tags


async def _get_or_create_tag_id(session, text: str) -> int:
    normalized = text.strip()
    existing = await session.scalar(select(Tag).where(Tag.text == normalized))
    if existing:
        return existing.tag_id

    tag = Tag(text=normalized)
    session.add(tag)
    await session.flush()
    return tag.tag_id


async def _save_meme_with_tags(file_id: str, media_type: str, caption: str, tags: list[str]) -> int:
    async with async_session() as session:
        meme = Meme(file_id=file_id, media_type=media_type, caption=caption)
        session.add(meme)
        await session.flush()  # получаем meme_id

        for tag_text in tags:
            tag_id = await _get_or_create_tag_id(session, tag_text)
            session.add(MemeTag(meme_id=meme.meme_id, tag_id=tag_id))

        await session.commit()
        return meme.meme_id


def _is_allowed(message: Message) -> bool:
    if message.chat.id != ADMIN_CHAT_ID:
        return False
    if not ALLOWED_ADMIN_USER_IDS:
        return True
    return message.from_user and message.from_user.id in ALLOWED_ADMIN_USER_IDS


@router.message(
    (F.photo | F.animation | F.video)  # поддержка фото/гиф/видео
)
async def ingest_meme(message: Message):
    if not _is_allowed(message):
        return

    caption = (message.caption or "").strip()
    if not caption:
        await message.reply("❌ Нужна подпись с тегами через запятую.\nПример: `грустный кот, работа, утро`")
        return

    tags = _parse_tags_from_caption(caption)
    if not tags:
        await message.reply("❌ Не нашёл теги в подписи. Укажи теги через запятую.")
        return

    if message.photo:
        file_id = message.photo[-1].file_id  # самое большое фото
        media_type = "photo"
    elif message.animation:
        file_id = message.animation.file_id
        media_type = "gif"
    else:  # video
        file_id = message.video.file_id
        media_type = "video"

    meme_id = await _save_meme_with_tags(
        file_id=file_id,
        media_type=media_type,
        caption=caption,
        tags=tags
    )

    await message.reply(f"✅ Сохранено: meme_id={meme_id}\n🏷 Теги: {', '.join(tags)}")
"""