import inspect
import pytest
from unittest.mock import AsyncMock


class _FakeScalarResult:
    def __init__(self, all_=None):
        self._all = list(all_ or [])

    def all(self):
        return list(self._all)

    def first(self):
        return self._all[0] if self._all else None


class _FakeSession:
    def __init__(self):
        self.scalar = AsyncMock()
        self.scalars = AsyncMock()
        self.execute = AsyncMock()
        self.commit = AsyncMock()
        self.flush = AsyncMock()
        self.add = AsyncMock()
        self.delete = AsyncMock()
        self.close = AsyncMock()


class _FakeSessionCM:
    def __init__(self, session: _FakeSession):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


def _patch_async_session(monkeypatch, module, session: _FakeSession):
    def _factory():
        return _FakeSessionCM(session)

    monkeypatch.setattr(module, "async_session", _factory, raising=False)


def _is_async_fn(obj) -> bool:
    return inspect.iscoroutinefunction(obj)


def test_db_requests_importable():
    import BOT.data_base.requests as rq
    assert rq is not None


def test_db_requests_has_async_functions_smoke():
    import BOT.data_base.requests as rq
    async_fns = [name for name, obj in vars(rq).items() if callable(obj) and _is_async_fn(obj)]
    assert async_fns, "В BOT.data_base.requests не найдено async-функций (странно для слоя БД)"


@pytest.mark.asyncio
async def test_db_get_favourites_user_not_found(monkeypatch):
    import BOT.data_base.requests as rq

    if not hasattr(rq, "db_get_favourites"):
        pytest.skip("Нет db_get_favourites в BOT.data_base.requests")

    session = _FakeSession()
    session.scalar.return_value = None  # user_id не найден

    _patch_async_session(monkeypatch, rq, session)

    favs = await rq.db_get_favourites(123)
    assert favs == []


@pytest.mark.asyncio
async def test_db_get_favourites_empty(monkeypatch):
    import BOT.data_base.requests as rq

    if not hasattr(rq, "db_get_favourites"):
        pytest.skip("Нет db_get_favourites в BOT.data_base.requests")

    session = _FakeSession()
    session.scalar.return_value = 1  # user_id найден
    session.scalars.return_value = _FakeScalarResult(all_=[])

    _patch_async_session(monkeypatch, rq, session)

    favs = await rq.db_get_favourites(123)
    assert favs == []


@pytest.mark.asyncio
async def test_db_get_favourites_non_empty(monkeypatch):
    import BOT.data_base.requests as rq

    if not hasattr(rq, "db_get_favourites"):
        pytest.skip("Нет db_get_favourites в BOT.data_base.requests")

    class MemeObj:
        def __init__(self, meme_id, file_id, media_type):
            self.meme_id = meme_id
            self.file_id = file_id
            self.media_type = media_type

    session = _FakeSession()
    session.scalar.return_value = 1
    session.scalars.return_value = _FakeScalarResult(
        all_=[MemeObj(10, "f1", "photo"), MemeObj(9, "f2", "gif")]
    )

    _patch_async_session(monkeypatch, rq, session)

    favs = await rq.db_get_favourites(123)
    assert len(favs) == 2
    assert favs[0].meme_id == 10


@pytest.mark.asyncio
async def test_db_search_memes_by_tags_smoke(monkeypatch):
    import BOT.data_base.requests as rq

    if not hasattr(rq, "db_search_memes_by_tags"):
        pytest.skip("Нет db_search_memes_by_tags в BOT.data_base.requests")

    class MemeObj:
        def __init__(self, meme_id, file_id, media_type):
            self.meme_id = meme_id
            self.file_id = file_id
            self.media_type = media_type

    session = _FakeSession()
    session.execute.return_value = None
    session.scalars.return_value = _FakeScalarResult(all_=[MemeObj(1, "f1", "photo")])

    _patch_async_session(monkeypatch, rq, session)

    try:
        res = await rq.db_search_memes_by_tags(["кот"], limit=1, used_ids=[])
    except TypeError:
        res = await rq.db_search_memes_by_tags(tag_texts=["кот"], used_ids=[], limit=1)

    assert isinstance(res, list)
