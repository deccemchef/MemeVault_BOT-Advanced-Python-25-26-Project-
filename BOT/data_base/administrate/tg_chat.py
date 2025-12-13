from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from data_base.models import async_session, Meme, Tag, MemeTag

router = Router()

ADMIN_CHAT_ID = -1003662277538


def parse_tags(caption: str) -> list[str]:
    tags = [t.strip() for t in caption.split(",") if t.strip()]
    seen = set()
    out = []
    for t in tags:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


async def get_or_create_tag_id(session, tag_text: str) -> int:
    tag = await session.scalar(select(Tag).where(Tag.text == tag_text))
    if tag:
        return tag.tag_id
    tag = Tag(text=tag_text)
    session.add(tag)
    await session.flush()
    return tag.tag_id


async def save_meme_with_tags(file_id: str, media_type: str, tags: list[str]) -> int:
    async with async_session() as session:
        meme = Meme(file_id=file_id, media_type=media_type)
        session.add(meme)
        await session.flush()

        for t in tags:
            tag_id = await get_or_create_tag_id(session, t)
            session.add(MemeTag(meme_id=meme.meme_id, tag_id=tag_id))

        await session.commit()
        return meme.meme_id


async def _ingest(message: Message):
    caption = (message.caption or "").strip()
    if not caption:
        await message.answer("❌ Добавь подпись с тегами через запятую. Пример: `кот, грусть, работа`")
        return

    tags = parse_tags(caption)
    if not tags:
        await message.answer("❌ Не нашёл теги. Укажи теги через запятую.")
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.animation:
        file_id = message.animation.file_id
        media_type = "gif"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    else:
        return

    meme_id = await save_meme_with_tags(file_id=file_id, media_type=media_type, tags=tags)
    await message.answer(f"✅ Сохранено: meme_id={meme_id}\n🏷 {', '.join(tags)}")


@router.channel_post(F.chat.id == ADMIN_CHAT_ID, (F.photo | F.animation | F.video))
async def ingest_from_channel(message: Message):
    await _ingest(message)


@router.message(F.chat.id == ADMIN_CHAT_ID, (F.photo | F.animation | F.video))
async def ingest_from_group(message: Message):
    await _ingest(message)