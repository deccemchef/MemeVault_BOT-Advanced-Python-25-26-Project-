from typing import Optional, List, Dict
from sqlalchemy.exc import IntegrityError
from constants import MAX_FAV
from sqlalchemy import select, func, delete
from data_base.models import async_session, Meme, Tag
from data_base.models import async_session, User, Favorite, Meme


async def ensure_user_exists(tg_id: int, username: str | None = None) -> None:
    async with async_session() as session:
        user_id = await session.scalar(
            select(User.user_id).where(User.telegram_id == tg_id)
        )
        if user_id is not None:
            return

        session.add(User(telegram_id=tg_id, username=username))

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def _get_user_id(session, tg_id: int) -> Optional[int]:
    return await session.scalar(
        select(User.user_id).where(User.telegram_id == tg_id)
    )


async def db_get_user_favourites(tg_id: int) -> List[Dict[str, str | None]]:
    async with async_session() as session:
        user_id = await _get_user_id(session, tg_id)
        if user_id is None:
            return []

        memes = (
            await session.scalars(
                select(Meme)
                .join(Favorite, Favorite.meme_id == Meme.meme_id)
                .where(Favorite.user_id == user_id)
            )
        ).all()

        return [
            {"file_id": m.file_id, "media_type": m.media_type}
            for m in memes
        ]


async def db_add_favourite(tg_id: int, meme_id: int) -> str:
    async with async_session() as session:
        user_id = await _get_user_id(session, tg_id)
        if user_id is None:
            return "NOUSER"

        count = await session.scalar(
            select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id)
        )
        if (count or 0) >= MAX_FAV:
            return "LIMIT"

        session.add(Favorite(user_id=user_id, meme_id=meme_id))

        try:
            await session.commit()
            return "OK"
        except IntegrityError:
            await session.rollback()
            return "EXISTS"


async def db_get_favourites(tg_id: int) -> list[Meme]:
    async with async_session() as session:
        user_id = await session.scalar(select(User.user_id).where(User.telegram_id == tg_id))
        if user_id is None:
            return []

        res = await session.scalars(
            select(Meme)
            .join(Favorite, Favorite.meme_id == Meme.meme_id)
            .where(Favorite.user_id == user_id)
            .order_by(Meme.meme_id.desc())
        )
        return res.all()


async def db_delete_favourite(tg_id: int, meme_id: int) -> str:
    async with async_session() as session:
        user_id = await session.scalar(select(User.user_id).where(User.telegram_id == tg_id))
        if user_id is None:
            return "NOUSER"

        result = await session.execute(
            delete(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.meme_id == meme_id
            )
        )
        await session.commit()

        deleted = getattr(result, "rowcount", 0) or 0
        return "OK" if deleted > 0 else "NOTFOUND"


async def db_search_memes_by_tags(tag_texts, limit, used_ids):
    if not tag_texts:
        return []

    tag_texts = [tag.lower() for tag in tag_texts]
    used_ids = used_ids or []

    async with async_session() as session:
        new_memes = (
            select(Meme)
            .join(Meme.tags)
            .where(Tag.text.in_(tag_texts))
        )

        if used_ids:
            new_memes = new_memes.where(Meme.meme_id.notin_(used_ids))

        new_memes = (
            new_memes.group_by(Meme.meme_id)
            .order_by(func.random())
            .limit(limit)
        )

        result = await session.scalars(new_memes)
        return result.all()


async def db_clear_favourites(tg_id: int) -> int | None:
    async with async_session() as session:
        user_id = await session.scalar(
            select(User.user_id).where(User.telegram_id == tg_id)
        )
        if user_id is None:
            return None

        result = await session.execute(
            delete(Favorite).where(Favorite.user_id == user_id)
        )
        await session.commit()

        return (getattr(result, "rowcount", 0) or 0)