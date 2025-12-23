import pytest
from unittest.mock import AsyncMock

from tests.conftest import DummyState


def _patch_search(monkeypatch, module, result):
    if hasattr(module, "db_search_memes_by_tags"):
        monkeypatch.setattr(
            module,
            "db_search_memes_by_tags",
            AsyncMock(return_value=result),
            raising=False,
        )

    if hasattr(module, "rq") and hasattr(module.rq, "db_search_memes_by_tags"):
        monkeypatch.setattr(
            module.rq,
            "db_search_memes_by_tags",
            AsyncMock(return_value=result),
            raising=False,
        )


def test_meme_service_importable():
    import BOT.services.meme_service as s
    assert s is not None


def test_generate_ngrams_if_exists():
    import BOT.services.meme_service as s

    if not hasattr(s, "generate_ngrams"):
        pytest.skip("generate_ngrams не найден в meme_service.py")

    assert s.generate_ngrams(["a", "b", "c"]) == ["a", "a b", "a b c", "b", "b c", "c"]
    assert s.generate_ngrams(["cat"]) == ["cat"]
    assert s.generate_ngrams([]) == []


@pytest.mark.asyncio
async def test_memes_start_sets_state_and_prompts():
    import BOT.services.meme_service as s

    if not hasattr(s, "memes_start"):
        pytest.skip("memes_start не найден в meme_service.py")

    msg = type("M", (), {})()
    msg.answer = AsyncMock()

    state = DummyState()

    await s.memes_start(msg, state)

    state.set_state.assert_awaited()
    msg.answer.assert_awaited()


@pytest.mark.asyncio
async def test_memes_get_query_empty_text():
    import BOT.services.meme_service as s

    if not hasattr(s, "memes_get_query"):
        pytest.skip("memes_get_query не найден в meme_service.py")

    msg = type("M", (), {})()
    msg.text = "   "
    msg.answer = AsyncMock()
    msg.answer_media_group = AsyncMock()

    state = DummyState()

    await s.memes_get_query(msg, state)

    msg.answer.assert_awaited()
    msg.answer_media_group.assert_not_awaited()


@pytest.mark.asyncio
async def test_memes_get_query_not_found(monkeypatch):
    import BOT.services.meme_service as s

    msg = type("M", (), {})()
    msg.text = "кот"
    msg.answer = AsyncMock()
    msg.answer_media_group = AsyncMock()

    state = DummyState(data={})

    if hasattr(s, "db_search_memes_by_tags"):
        monkeypatch.setattr(s, "db_search_memes_by_tags", AsyncMock(return_value=[]), raising=False)
    elif hasattr(s, "rq") and hasattr(s.rq, "db_search_memes_by_tags"):
        monkeypatch.setattr(s.rq, "db_search_memes_by_tags", AsyncMock(return_value=[]), raising=False)
    else:
        pytest.skip("Не нашёл где мокать db_search_memes_by_tags")

    await s.memes_get_query(msg, state)

    state.clear.assert_not_awaited()
    msg.answer_media_group.assert_not_awaited()

    assert msg.answer.called, "Ожидали, что message.answer будет вызван (даже если без await)"


@pytest.mark.asyncio
async def test_memes_get_query_found(monkeypatch):
    import BOT.services.meme_service as s

    if not hasattr(s, "memes_get_query"):
        pytest.skip("memes_get_query не найден в meme_service.py")

    class MemeObj:
        def __init__(self, meme_id, file_id, media_type):
            self.meme_id = meme_id
            self.file_id = file_id
            self.media_type = media_type

    msg = type("M", (), {})()
    msg.text = "cat"
    msg.answer = AsyncMock()
    msg.answer_media_group = AsyncMock()

    state = DummyState(data={})

    found = [
        MemeObj(1, "file1", "photo"),
        MemeObj(2, "file2", "gif"),
    ]
    _patch_search(monkeypatch, s, result=found)

    await s.memes_get_query(msg, state)

    msg.answer_media_group.assert_awaited()
    msg.answer.assert_awaited()

    data = await state.get_data()

    if "last_batch_ids" in data:
        assert data["last_batch_ids"] == [1, 2]
    if "last_batch_count" in data:
        assert data["last_batch_count"] == 2
