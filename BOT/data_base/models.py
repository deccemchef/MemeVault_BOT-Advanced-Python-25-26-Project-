from typing import Optional, List

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    favorites: Mapped[List["Favorite"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Meme(Base):
    __tablename__ = "memes"

    meme_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    media_type: Mapped[str] = mapped_column(String(16), nullable=False, default="photo")

    favorites: Mapped[List["Favorite"]] = relationship(
        back_populates="meme", cascade="all, delete-orphan"
    )

    tags: Mapped[List["Tag"]] = relationship(
        secondary="meme_tags",
        back_populates="memes",
        lazy="selectin",
    )


class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    memes: Mapped[List["Meme"]] = relationship(
        secondary="meme_tags",
        back_populates="tags",
        lazy="selectin",
    )


class MemeTag(Base):
    __tablename__ = "meme_tags"

    meme_id: Mapped[int] = mapped_column(
        ForeignKey("memes.meme_id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.tag_id", ondelete="CASCADE"),
        primary_key=True,
    )


class Favorite(Base):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    meme_id: Mapped[int] = mapped_column(
        ForeignKey("memes.meme_id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(back_populates="favorites")
    meme: Mapped["Meme"] = relationship(back_populates="favorites")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
