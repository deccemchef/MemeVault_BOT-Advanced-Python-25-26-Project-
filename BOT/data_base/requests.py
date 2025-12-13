from typing import Optional, List, Dict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

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
            {"file_id": m.file_id, "caption": m.caption, "media_type": m.media_type}
            for m in memes
        ]


async def db_add_favourite(tg_id: int, meme_id: int) -> bool:
    async with async_session() as session:
        user_id = await _get_user_id(session, tg_id)
        if user_id is None:
            return False

        session.add(Favorite(user_id=user_id, meme_id=meme_id))

        try:
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False
